int main(int argc, char* argv)
{
	int sum = 0;
	int n = 0;
    n = atoi(argv[2]);
	int* a;
	a = malloc(sizeof(int)*n);
	if(argc > 2){
	  sum = a[0] + 2;
	} else {
	  sum = a[0];
	}
	k = 1;
	for (i = 0; i < n; i++) {
		sum += a[i];
	}

	return sum;
}

int main2(int argc, char* argv)
{
	int sum = 0;
	int n = 0;
    n = atoi(argv[2]);
	int* a;
	a = malloc(sizeof(int)*n);
	if(argc > 2){
	  sum = a[0] + 2;
	}
	k = 1;
	for (i = 0; i < n; i++) {
		sum += a[i];
	}

	return sum;
}

int main3(int argc, char* argv)
{
	int sum = 0;
	int n = 0;
    n = atoi(argv[2]);
	int* a;
	a = malloc(sizeof(int)*n);
	if(argc > 2){
	  sum = a[0] + 2;
	}
	k = 1;
	for (i = 0; i < n; i++) {
		sum += a[i];
	}

	while(k < n) {
	  sum = sum - k;
	  k++;
	};
	return sum;
}

int main4(int argc, char* argv)
{
	int sum = 0;
	int n = 0;
    n = atoi(argv[2]);
	int* a;
	a = malloc(sizeof(int)*n);
	if(argc > 2){
	  sum = a[0] + 2;
	}
	k = 1;
	for (i = 0; i < n; i++) {
		sum += a[i];
		while(k < n) {
	      sum = sum - k;
	      k++;
	    };
	}
	return sum;
}

int comp_msq(int n, int** a)
{
  int i, j;
  int p, msq;
  int* c, b;
  msq = 0;
  c = malloc(sizeof(int) * n);
  b = malloc(sizeof(int) * n);

  for(i=0; i<n; i++){
    for(j=0; j<n; j++){
      if (a[i][j] == 0) {
	c[j] = 0;
      } else {
	p = min (c[j-1], c[j]);
	if (b[i-p, j-p] !=0) {
	  c[j] = p;
	} else {
	  c[j] = p+1;
	}
      }
      msq = max(c[j], msq);
    }
  }
  return msq;
}

