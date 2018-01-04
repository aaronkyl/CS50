/**
 * Resizes a bitmap file.
 */
       
#include <stdio.h>
#include <stdlib.h>

#include "bmp.h"

int main(int argc, char *argv[]){

    // ensure proper usage
    if(argc != 4 || atoi(argv[1]) < 1 || atoi(argv[1]) > 100){
        fprintf(stderr, "Usage: ./resize n infile outfile (where n between 1 and 100, inclusive)\n");
        return 1;
    }

    // remember filenames
    char *infile = argv[2];
    char *outfile = argv[3];
    
    // remember resize factor
    int n = atoi(argv[1]);

    // open input file 
    FILE *inptr = fopen(infile, "r");
    if(inptr == NULL){
        fprintf(stderr, "Could not open %s.\n", infile);
        return 2;
    }

    // open output file
    FILE *outptr = fopen(outfile, "w");
    if(outptr == NULL){
        fclose(inptr);
        fprintf(stderr, "Could not create %s.\n", outfile);
        return 3;
    }

    // read infile's BITMAPFILEHEADER
    BITMAPFILEHEADER bf;
    fread(&bf, sizeof(BITMAPFILEHEADER), 1, inptr);

    // read infile's BITMAPINFOHEADER
    BITMAPINFOHEADER bi;
    fread(&bi, sizeof(BITMAPINFOHEADER), 1, inptr);

    // ensure infile is (likely) a 24-bit uncompressed BMP 4.0
    if(bf.bfType != 0x4d42 || bf.bfOffBits != 54 || bi.biSize != 40 || 
        bi.biBitCount != 24 || bi.biCompression != 0){
        fclose(outptr);
        fclose(inptr);
        fprintf(stderr, "Unsupported file format.\n");
        return 4;
    }
    
    // remember source file's width and height and padding
    int source_height = abs(bi.biHeight);
    int source_width = abs(bi.biWidth);
    int source_padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    
    // modify width and height in BITMAPINFOHEADER
    bi.biWidth *= n;
    bi.biHeight *= n;
    
    // determine padding for scanlines
    int resized_padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    
    // modify SizeImage in BITMAPINFOHEADER
    bi.biSizeImage = ((sizeof(RGBTRIPLE) * bi.biWidth) + resized_padding) * abs(bi.biHeight);
    
    //modify size in BITMAPFILEHEADER
    bf.bfSize = bi.biSizeImage + sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);

    // write outfile's BITMAPFILEHEADER
    fwrite(&bf, sizeof(BITMAPFILEHEADER), 1, outptr);

    // write outfile's BITMAPINFOHEADER
    fwrite(&bi, sizeof(BITMAPINFOHEADER), 1, outptr);

    // iterate over infile's scanlines
    for(int i = 0; i < source_height; i++){
        // repeat each line n times
        for(int j = 0; j < n; j++){
            // iterate over pixels in scanline
            for(int k = 0; k < source_width; k++){
                // temporary storage for pixel and counter
                RGBTRIPLE triple;
                int pixel_repeater = 0;
                
                // read RGB triple from infile
                fread(&triple, sizeof(RGBTRIPLE), 1, inptr);
                
                // write RGB triple to outfile n times
                while(pixel_repeater < n){
                    fwrite(&triple, sizeof(RGBTRIPLE), 1, outptr);
                    pixel_repeater++;
                }
            }
            
            // add padding to the line
            for(int k = 0; k < resized_padding; k++){
                fputc(0x00, outptr);
            }
            
            // move indicator in infile back to beginning of line
            // as long as this is not the last repeated line
            if(j < n - 1)
                fseek(inptr, (source_width * -3), SEEK_CUR);
        }

        // skip over padding, if any
        fseek(inptr, source_padding, SEEK_CUR);
    }

    // close infile
    fclose(inptr);

    // close outfile
    fclose(outptr);

    // success
    return 0;
}
