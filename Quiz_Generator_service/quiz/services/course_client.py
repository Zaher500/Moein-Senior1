import os
import requests
from io import BytesIO

def fetch_lecture_file(lecture_id):
    course_service_url = os.getenv('COURSE_SERVICE_URL', 'http://localhost:8002')
    url = f"{course_service_url}/api/lectures/{lecture_id}/file/"
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Try to get the filename from the disposition header
        content_disposition = response.headers.get('content-disposition', '')
        filename = f"lecture_{lecture_id}.pdf"  # Fallback
        
        if "filename=" in content_disposition:
            # Simple parsing for standard disposition header
            filename = content_disposition.split("filename=")[1].strip('"\'')
            
        file_obj = BytesIO(response.content)
        file_obj.name = filename
        
        return file_obj, filename
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch lecture file from Course Service: {str(e)}")
