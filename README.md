# OgreMeshNormalFixes
Scripts to automatically fix Ogre Meshes with messed up normals. Uses Ogre CLI tools. 

Primary Tools

    OgreXMLConverter.exe - Official Ogre tool for converting between .mesh and .xml formats
    recalculate_normals.py - Custom Python script for recalculating vertex normals
    ogre_normal_batch.bat - Automated batch processing script


Requirements

    Python 3.x - For running recalculate_normals.py
    Ogre Command Line Tools 1.11.6 - Critical for BZR compatibility
    Windows Command Prompt - For running batch scripts


When to Use These Tools

Use the Ogre CLI tools when your converted models have:

    Incorrect lighting - Models appear too dark or bright in certain areas
    Shading artifacts - Strange shadows or lighting discontinuities
    Faceted appearance - Models look angular when they should be smooth
    Normal vector issues - Detected during model validation


Workflow Integration

Complete Model Conversion Process
1. Use port_models.py to convert vdf/sdf/odf → mesh/skeleton/material
2. Use Ogre CLI tools to fix normals in .mesh files
3. Deploy all files to your mod folder

recalculate_normals.py

Purpose
A specialized Python script that recalculates vertex normals from face geometry data in Ogre mesh XML files. This fixes lighting issues by ensuring normals point in the correct directions.

Usage
python recalculate_normals.py <mesh.xml file>

How It Works

    Parses Ogre mesh XML files
    Calculates face normals using cross products of triangle edges
    Accumulates and averages normals for each vertex
    Normalizes vectors to unit length
    Updates the XML with corrected normal data


Example Usage
python recalculate_normals.py mytank.mesh.xml

Output
Processing: mytank.mesh.xml
  Processing submesh 1...
    Updated 1247 normals from 582 faces
  Successfully recalculated normals for 1247 vertices
Normal recalculation completed successfully

Technical Details

    Algorithm: Face-weighted normal averaging
    Precision: 6 decimal places for normal coordinates
    Validation: Handles degenerate triangles and invalid indices
    Fallback: Uses (0,1,0) up vector for vertices without faces


ogre_normal_batch.bat

Purpose
Automated batch processing script that processes all .mesh files in a directory, handling the complete workflow from mesh conversion to normal recalculation.

Features

    Automatic backup - Creates backup/ directory with original files
    Batch processing - Handles all .mesh files in current directory
    Error handling - Continues processing even if individual files fail
    Progress tracking - Shows detailed status for each file
    File validation - Checks output file sizes for corruption
    Cleanup - Removes temporary .xml files after processing


Usage

    Place the script in the directory containing your .mesh files
    Ensure recalculate_normals.py is in the same directory
    Ensure OgreXMLConverter.exe is in your PATH or same directory
    Double-click the .bat file or run from command prompt


Automated Workflow
For each .mesh file, the script:
1. Creates backup → backup/filename.mesh.backup
2. Converts mesh to XML → OgreXMLConverter.exe file.mesh file.mesh.xml
3. Recalculates normals → python recalculate_normals.py file.mesh.xml
4. Converts back to mesh → OgreXMLConverter.exe file.mesh.xml file.mesh
5. Validates output file size
6. Cleans up temporary XML file
