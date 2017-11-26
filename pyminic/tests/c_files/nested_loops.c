void heateqn(int* a, int m, int n){
  int i;
  int j;
  for(i = 0; i< n; i++){
    for(j = 0; j < n; j++) {
      a[i] = (a[i - 1] + a[i] + a[i + 1]) / 3;
    }
  }
}

void stencil2D(int** a, int m, int n){
  int i;
  int j;
  for(i = 0; i< n; i++){
    for(j = 0; j < n; j++) {
      a[i][j-1] *= 2;
      a[i][j] = (a[i - 1][j-1] + a[i][j-1] + a[i + 1][j-1]) / 3;
    }
  }
}

void smooth2D(int** a, int m, int n){
  int t = 0;
  int i;
  int j;
  for(t = 0; t < steps; t++){
    for(i = 0; i< n; i++){
      for(j = 0; j < n; j++) {
	a[i][j] = (5*a[i][j] + 3*a[i][j-1] + 3*a[i][j+1] +
		   3*a[i-1][j] + a[i-1][j-1] + a[i-1][j+1] +
		   3*a[i+1][j] + a[i+1][j-1] + a[i+1][j+1]) / 21;
      }
    }
  }
}
