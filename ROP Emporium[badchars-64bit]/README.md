# badchars - 64 bit

we are progressing in the series and the challanges are becoming more interesting.  
     
this time we have to deal with badchars.
    
badchars are characters that will not appear in memory the way we expect them to     
and therefore will cause unexpected behaviour.    
     
for example: a null byte is the most common bad char as it will usually(not in this challange though) terminate strings. 
    
we are granted with a list of bad chars when we execute the binary. 
    
![begin](https://user-images.githubusercontent.com/60041914/78296351-3a98d600-7536-11ea-99f1-b680518e923f.png)
   
when checking out the gadgets we should look for ways to bypass this constraint.    
it's time to get creative.
