/**
 * helpers.c
 *
 * Helper functions for Problem Set 3.
 */
 
#include <cs50.h>

#include "helpers.h"

/**
 * Returns true if value is in array of n values, else false.
 */
bool search(int value, int values[], int n)
{
    // TODO: implement a searching algorithm
    if (n > 0) {
        int mid = n / 2;
        if (values[mid] == value) {
            return true;
        } else if (mid > 0 && value < values[mid]) {
            int subarray[mid];
            for (int i = 0; i < mid; i++) {
                subarray[i] = values[i];
            }
            return search(value, subarray, mid);
        } else if (mid > 0 && value > values[mid]) {
            int subarray_length;
            if (n % 2 == 0) {
                subarray_length = mid - 1;
                if (subarray_length == 0) {
                    return false;
                }
            } else {
                subarray_length = mid;
            }
            int subarray[subarray_length];
            for (int i = mid + 1, k = 0; i < n; i++, k++) {
                subarray[k] = values[i];
            }
            return search(value, subarray, subarray_length);
        }
    }
    return false;
}

/**
 * Sorts array of n values.
 */
void sort(int values[], int n)
{
    // TODO: implement a sorting algorithm
    int counting[65535] = {0};
    
    for (int i = 0; i < n; i++) {
        counting[values[i]]++;
    }
    
    int result_position = 0;
    
    for (int i = 0; i < 65535; i++) {
        if (counting[i] > 0) {
            for (int k = 0; k < counting[i]; k++, result_position++) {
                values[result_position] = i;
            }
        }
    }
}