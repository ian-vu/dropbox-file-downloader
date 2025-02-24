import requests
import json
import argparse
import os

def main(args):
    # Define the API URLs
    list_folder_url = "https://api.dropboxapi.com/2/files/list_folder"
    get_shared_link_file_url = "https://content.dropboxapi.com/2/sharing/get_shared_link_file"

    # Access token from arguments
    access_token = args.token

    # Shared link from arguments
    shared_link = args.url

    # Headers for the API requests
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Parameters for list folder request
    list_folder_params = {
        "path": "",
        "shared_link": {"url": shared_link}
    }

    print("Fetching file list...")
    response = requests.post(list_folder_url, json=list_folder_params, headers=headers)
    data = response.json()

    # If verbose mode is on, print the whole response data
    if args.verbose:
        print("Verbose info: ", data)

    entries = data.get("entries", [])

    if len(entries) > 0:
        total_files = len(entries) if args.count is None else min(len(entries), args.count)
        print(f"Total files to download: {total_files}")

        for i, file_info in enumerate(entries):
            if args.count is not None and i >= args.count:
                break

            file_name = file_info["name"]
            download_path = os.path.join(args.download_folder, file_name)

            # Check if the file already exists
            if os.path.exists(download_path):
                print(f"File {i+1} of {total_files}: {file_name} already exists, skipping.")
                continue

            print(f"Downloading file {i+1} of {total_files}: {file_name}...")

            # Parameters for get shared link file request
            get_shared_link_file_params = {
                "path": f"/{file_name}",
                "url": shared_link
            }

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Dropbox-API-Arg": json.dumps(get_shared_link_file_params)
            }

            response = requests.post(get_shared_link_file_url, headers=headers)
            content = response.content

            with open(download_path, "wb") as f:
                f.write(content)

            print(f"Download complete. File saved as: {download_path}")
    else:
        print("No files found in the shared folder.")


if __name__ == "__main__":
    # Creating argument parser
    parser = argparse.ArgumentParser(description='Download files from a shared Dropbox folder.')

    # Adding arguments
    parser.add_argument('-t', '--token', type=str, required=True, help='Access token for Dropbox API.')
    parser.add_argument('-url', type=str, required=True, help='Shared Dropbox folder link.')
    parser.add_argument('-df', '--download_folder', default='downloads', help='Download folder. Default is "downloads".')
    parser.add_argument('-c', '--count', type=int, help='Number of files to download. If not provided, all files will be downloaded.')
    parser.add_argument("--h", action="help", help="Show all listed options with a brief English description.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode to print the full API response.")

    # Parsing arguments
    args = parser.parse_args()

    # Create the download folder if not exists
    if not os.path.exists(args.download_folder):
        os.makedirs(args.download_folder)

    # Running main function
    main(args)
