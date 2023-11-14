#!/bin/bash

# Create an empty file for the final output
output_file="concatenated_output.txt"
> "$output_file"

# Loop through all .txt files in the current directory
for file in *.txt; do
    # Check if the file is not the output file to avoid self-inclusion
    if [ "$file" != "$output_file" ]; then
        # Add the file name as a header
        echo "File: $file" >> "$output_file"
        echo "----------------" >> "$output_file"
        
        # Process the file content
        while IFS= read -r line; do
            # Check for the separator "-----"
            if [[ "$line" == *"-----"* ]]; then
                # Replace the separator with "Answer:"
                echo "Content:" >> "$output_file"
            else
                # Add "Question:" only before the first line of the file content
                if [[ ! $question_added ]]; then
                    echo "Topic:" >> "$output_file"
                    question_added=true
                fi
                echo "$line" >> "$output_file"
            fi
        done < "$file"
        unset question_added
        
        # Add a separator between files
        echo -e "\n\n-----\n\n" >> "$output_file"
    fi
done

echo "Concatenation complete. Output is in $output_file"
