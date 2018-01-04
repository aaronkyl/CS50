#include <stdio.h>
#include <stdint.h>

#define BUFFER_SIZE 512

int main(int argc, char *argv[]){
    
    // confirm user entered only one argument
    if(argc != 2){
        fprintf(stderr, "Usage: ./recover file-to-recover. Terminating program.\n");
        return 1;
    }
    
    // open infile (rawfile is pointer)
    FILE *rawfile = fopen(argv[1], "r");
    
    // confirm infile readable
    if (rawfile == NULL){
        fprintf(stderr, "Unable to open %s. Terminating program.\n", argv[1]);
        return 2;
    }
    
    // initialize jpeg count, used to track if any jpegs found and for filename numbering
    int jpg_count = 0;
    
    // create buffer for infile reading
    unsigned char buffer[BUFFER_SIZE];
    FILE *img = NULL;
    int jpg_found = 0;
    
    // while current chunk is 512 bytes
    while(fread(buffer, BUFFER_SIZE, 1, rawfile)){
        // check if current chunk is the start of a jpg
        if(buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] & 0xf0) == 0xe0){
            // indicate start of jpgs found
            jpg_found = 1;
            
            // if this is not the first jpg found, close open image file
            if(jpg_count != 0){
                fclose(img);
            }
            
            // prepare new output jpg file (img is pointer)
            char filename[8];
            sprintf(filename, "%03i.jpg", jpg_count++);
            img = fopen(filename, "wa");
        }
        if(jpg_found)
            // write current chunk to output jpg file
            fwrite(buffer, BUFFER_SIZE, 1, img);
    }
    
    // close raw file and last image file
    fclose(rawfile);
    fclose(img);
}