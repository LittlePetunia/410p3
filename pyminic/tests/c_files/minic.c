int mss(int *a, int n){
    int mss = 0;
    int mts = 0;
    int sum = 0;
    for(int i = 0; i < n; ++i) {
        sum += a[i];
        mts = max(mts + a[i], 0);
        mss = max(mts, mss);
    }
    return mss;
}

int main(int argc, char** argv){
    int n = 1000;
    int* a;
    a = malloc(n * sizeof(a));
    return mss(a, n);
}