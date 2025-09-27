#!/usr/bin/env python3
"""
CSV to XML Converter for PS4 Module Loading

Converts a CSV file with 'obf' and 'sym' columns to XML format.
The CSV should have two columns: obf (obfuscated name) and sym (symbol name).
The output XML follows the DynlibDatabase format with Entry elements.

Input: aerolib.csv from https://github.com/SocraticBliss/ps4_module_loader
Output: ps4database.xml for https://github.com/jogolden/GhidraPS4Loader

"""

import csv
import xml.etree.ElementTree as ET
import xml.dom.minidom
import argparse
import sys
from pathlib import Path


def csv_to_xml(csv_file_path, xml_file_path=None):
    """
    Convert CSV file to XML format.
    
    Args:
        csv_file_path (str): Path to input CSV file
        xml_file_path (str): Path to output XML file (optional)
    
    Returns:
        str: XML content as string
    """
    # Create root element
    root = ET.Element("DynlibDatabase")
    
    try:
        # Read CSV file
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ')
            
            # Skip header if present (check if first row contains 'obf' and 'sym')
            first_row = next(reader, None)
            if first_row and len(first_row) >= 2:
                if first_row[0].lower() != 'obf' and first_row[1].lower() != 'sym':
                    # First row is data, not header - process it
                    obf, sym = first_row[0].strip(), first_row[1].strip()
                    if obf and sym:  # Only add if both values are non-empty
                        entry = ET.SubElement(root, "Entry")
                        entry.set("obf", obf)
                        entry.set("lib", "null")
                        entry.set("sym", sym)
            
            # Process remaining rows
            for row in reader:
                if len(row) >= 2:
                    obf, sym = row[0].strip(), row[1].strip()
                    if obf and sym:  # Only add if both values are non-empty
                        entry = ET.SubElement(root, "Entry")
                        entry.set("obf", obf)
                        entry.set("lib", "null")
                        entry.set("sym", sym)
                        
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None
    
    # Convert to string with proper formatting
    rough_string = ET.tostring(root, encoding='unicode')
    
    # Format XML with proper indentation
    try:
        reparsed = xml.dom.minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        # Clean up the formatting - remove empty lines and fix declaration
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        formatted_xml = '\n'.join(lines)
    except:
        # Fallback to simple formatting if minidom fails
        formatted_xml = '<?xml version="1.0"?>\n' + rough_string
    
    # Write to file if output path specified
    if xml_file_path:
        try:
            with open(xml_file_path, 'w', encoding='utf-8') as xmlfile:
                xmlfile.write(formatted_xml)
            print(f"XML file saved to: {xml_file_path}")
        except Exception as e:
            print(f"Error writing XML file: {e}")
            return None
    
    return formatted_xml


def main():
    parser = argparse.ArgumentParser(
        description='Convert CSV file to XML format for DynlibDatabase'
    )
    parser.add_argument('input_csv', nargs='?', default='aerolib.csv',
                       help='Input CSV file path (default: aerolib.csv)')
    parser.add_argument('-o', '--output', help='Output XML file path (default: ps4database.xml)')
    parser.add_argument('--print', action='store_true', 
                       help='Print XML to stdout instead of/in addition to file')
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not Path(args.input_csv).exists():
        print(f"Error: Input file '{args.input_csv}' does not exist.")
        sys.exit(1)
    
    # Use ps4database.xml as default output filename
    output_file = args.output
    if not output_file and not args.print:
        output_file = 'ps4database.xml'
    
    # Convert CSV to XML
    xml_content = csv_to_xml(args.input_csv, output_file)
    
    if xml_content is None:
        sys.exit(1)
    
    # Print to stdout if requested
    if args.print:
        print("\nGenerated XML:")
        print(xml_content)


if __name__ == "__main__":
    main()