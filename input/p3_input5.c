void test(){
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
}	
