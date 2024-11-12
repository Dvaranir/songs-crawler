import os

def replace_underscores_with_spaces(directory):
    # List all files in the specified directory
    files = os.listdir(directory)

    for file_name in files:
        # Check if the file name contains underscores
        if '_' in file_name:
            # Replace underscores with spaces
            new_name = file_name.replace('_', ' ')
            
            # Construct the full path for the old and new file names
            old_path = os.path.join(directory, file_name)
            new_path = os.path.join(directory, new_name)

            # Rename the file
            os.rename(old_path, new_path)
            print(f'Renamed: {old_path} to {new_path}')

# Replace underscores with spaces in the current working directory
replace_underscores_with_spaces('.')