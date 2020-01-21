
# LowDeep[EASY]
LowDeep was an introductory-level challange at the Insomni'hack teaser 2020.   
We are presented with a simple web app that allows us to ping a host.  
Trying simple command injection with ';' we see there is no filtering.  
(Note the print-flag file)
![‏‏צילום מסך (34)](https://user-images.githubusercontent.com/60041914/72793602-57b24e00-3c43-11ea-9c9c-2d4fe746cbd6.png)
(it works!)  
   
   
however, cat is blocked.
![‏‏צילום מסך (35)](https://user-images.githubusercontent.com/60041914/72793609-597c1180-3c43-11ea-9ad1-c26f64dd2559.png)

after downloading the file we see it's an ELF binary. 
we can run strings on it and get the flag.
![‏‏צילום מסך (36)](https://user-images.githubusercontent.com/60041914/72793717-7fa1b180-3c43-11ea-9d15-5224ab523bb6.png)

