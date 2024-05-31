from urllib.parse import urlparse, parse_qs

def get_original_name(resource_url):
    # Parse the URL
    parsed_url = urlparse(resource_url)

    # Extract the path
    path = parsed_url.path

    # Extract the image name
    orignal_name = path.split('/')[-1]

    return orignal_name
