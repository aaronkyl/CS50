#include <stdio.h>
#include <stdlib.h>
#include "bmp.h"


int main(int argc, char *argv[]) {       // using char* instead of string since not using cs50.h
    
    // ensure user provided both input file and output files
    if (argc != 3) {
        fprintf(stderr, "Usage: ./whodunit infile outfile\n");
        return 1;
    }
    
    // open input file for reading
    FILE *infile = fopen(argv[1], "r");
    if (infile == NULL) {
        fprintf(stderr, "Unable to open %s. Terminating program.\n", argv[1]);
        return 2;
    }
    
    // open output file for writing
    FILE *outfile = fopen(argv[2], "w");
    if (outfile == NULL) {
        fclose(infile);
        fprintf(stderr, "Unable to open %s. Terminating program.\n", argv[2]);
        return 3;
    }
    
    // read infile's BITMAPFILEHEADER
    BITMAPFILEHEADER bmfh;
    fread(&bmfh, sizeof(BITMAPFILEHEADER), 1, infile);

    // read infile's BITMAPINFOHEADER
    BITMAPINFOHEADER bmih;
    fread(&bmih, sizeof(BITMAPINFOHEADER), 1, infile);

    // check that input was 24-bit uncompressed bitmap
    if (bmfh.bfType != 0x4D42 || bmfh.bfOffBits != 54 || bmih.biSize != 40 || 
        bmih.biBitCount != 24 || bmih.biCompression != 0)
    {
        fclose(outfile);
        fclose(infile);
        fprintf(stderr, "Must use 24-bit uncompressed bitmap!\n");
        return 4;
    }
    
    // write outfile's BITMAPFILEHEADER
    fwrite(&bmfh, sizeof(BITMAPFILEHEADER), 1, outfile);

    // write outfile's BITMAPINFOHEADER
    fwrite(&bmih, sizeof(BITMAPINFOHEADER), 1, outfile);
    
    // determine padding for scanlines
    int padding =  (4 - (bmih.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    
    // iterate over infile's scanlines
    for (int i = 0, height = abs(bmih.biHeight); i < height; i++) {
        
        // iterate over each pixel on the line
        for (int j = 0, width = bmih.biWidth; j < width; j++) {
            
            // create temporary holding variable
            RGBTRIPLE temp;
            
            // read a pixel
            fread(&temp, sizeof(RGBTRIPLE), 1, infile);
            
            // remove the red from the pixel
            if (temp.rgbtBlue == 0x00 && temp.rgbtGreen == 0x00 && temp.rgbtRed == 0xFF) {
                temp.rgbtBlue = 0xFF;
                temp.rgbtGreen = 0xFF;
            }
            
            // write modified pixel to outfile
            fwrite(&temp, sizeof(RGBTRIPLE), 1, outfile);
        }
        
        // skip over padding in rest of line in infile
        fseek(infile, padding, SEEK_CUR);
        
        // add padding to outfile, if needed
        for (int k = 0; k < padding; k++) {
            fputc(0x00, outfile);
        }
    }
    
    fclose(infile);
    fclose(outfile);
    return 1;
    
}