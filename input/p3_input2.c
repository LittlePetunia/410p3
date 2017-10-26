void test(int* a, int b,int k, int c){
	if(b) {
		k = k + 1;
	} else {
		k = k - 1;
	}
	c = a[k];
}