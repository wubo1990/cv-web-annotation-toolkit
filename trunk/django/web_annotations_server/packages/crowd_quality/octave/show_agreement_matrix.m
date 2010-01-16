function show_agreement_matrix(agreement)

a=full(agreement);

colorblind=1;

if colorblind

  P=a.*(a>0);
  N=-a.*(a<0);
  W=0*(a==0);
  
  v=cat(3, P , W, N);

  imshow(v./max(v(:)),[]);colorbar

else
  P=(a>0);
  exP=(1-a).*(a>0);
  N=(a<0);
  exN=(1+a).*(a<0);
  
  W=(a==0);
  
  v=cat(3, W + P + exN , W+exN+exP, W + N+exP);
  
  imshow(v,[]);colorbar
end