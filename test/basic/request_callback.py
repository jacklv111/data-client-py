#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#

from cgi import parse_header

from data_client.utils import parser


def create_request_callback(self, necessary_keys, necessary_file_names):
    def request_callback(request, uri, response_headers):
        content_type = request.headers.get("Content-Type", "")
        is_multipart = content_type.startswith("multipart/form-data")
        
        if is_multipart:
            print("This is a multipart form request ---------------------------------")
            
            # Get the boundary string from the Content-Type header
            _, params = parse_header(content_type)
            boundary = params.get("boundary")
            
            # Parse the form data
            files = parser.parse_multipart_form_data(request, boundary)
            
            # Check for the necessary keys
            missing_keys = [file for file in necessary_keys if file not in files]
            file_name_set = set()
            
            self.assertTrue(not missing_keys)
            
            for field_name, file_list in files.items():
                print(f"{field_name}:")
                for idx, file_data in enumerate(file_list):
                    print(f"  File {idx+1}: {file_data['filename']}")
                    file_name_set.add(file_data['filename'])
            
            # Check for the necessary files
            for necessary_file in necessary_file_names:
                self.assertTrue(necessary_file in file_name_set)
        else:
            print("This is not a multipart form request.")
        return [200, response_headers, ""]
    return request_callback
