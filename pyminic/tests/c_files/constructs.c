int main(int argc, char **argv){
    int** a = {0};
    int n = 1000;
    _Bool b;
    a = malloc(sizeof(a) * n);

    for(i = 0; i < n; i++) {
        a[i] = malloc(sizeof(*a) * n);
    }

    freeall(a, n);
    return 0;
}

void freeall(int **a, int n){
    for(i = 0; i < n; i++) {
        free(a[i]);
    }
    free(a);
}