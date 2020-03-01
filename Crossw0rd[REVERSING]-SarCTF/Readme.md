# Crossw0rd

Was a challange at the SarCTF in the reversing category.
The program gets a password and validates it.
![‏‏צילום מסך (42)](https://user-images.githubusercontent.com/60041914/74608994-5cf1a400-50ee-11ea-81fe-b5a6c2ea28ff.png)
We can see that the value of eax after some function will determine the success of the validation.   

![‏‏צילום מסך (43)](https://user-images.githubusercontent.com/60041914/74608999-60852b00-50ee-11ea-9c70-5a091f7ec4a0.png)
We see that our input is compared at diffrent indexes to see if it's equal to some chars.
if it's equal eax will be set to 1 which will return a success status.   
before the return we see another function that has a similer structure.    
![‏‏צילום מסך (44)](https://user-images.githubusercontent.com/60041914/74609001-61b65800-50ee-11ea-8860-e4b0004c7112.png)

we can see it calls another function that probably does somthing similer...      
    
we can get the flag piece by piece. 


![‏‏צילום מסך (46)](https://user-images.githubusercontent.com/60041914/74609183-5fed9400-50f0-11ea-93d4-0b1f2ccf1f67.png)

## FLAG{3a5yr3v3r5ing}
