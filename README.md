# battles-script-generator
### A battles script generator designed to work with the OTFBM + Battle Planner extensions for AVRAE discord bot. 
UI is rather simple at the moment and code needs to be run in terminal or code editor, but improvements will be made over time. 

## How it works
### Step 1
Download the source code provided and keep the file sturcture the same. In input, please paste your bestiary and make sure it is called "bestiary.json" (without the quotation marks). I have provided one.
Please note that monster entries your bestiary needs the following format: 
```json
[{
        "name": "monsterName",
        "cr": "CR",
        "size": "Size",
        "shortcodeToken": ""
    }]
```
An example would be : 
```json
[{
        "name": "Goblin",
        "cr": "1/4",
        "size": "Small",
        "shortcodeToken": ""
    }]
```
As we see there is an empty directory called shortcodeToken that we will come back to later.

### Step 2

Run the code in terminal or in a python editor. Eventually I will improve the programme to run alone, but right now it hasn't been compiled and it outputs data to the terminal. 
You should be greeted with this :
![image](https://github.com/TheBenjameister/battles-script-generator/assets/82944215/c42ac776-2064-4ff4-a8e5-8b12fdc98ef9)
Here you can see a multitude of fields that we will be filling in for your encounter. 
Lets set one up together!

### Step 3 
I want to set up an encounter with 3 goblins and a goblin boss. To do so, lets start by naming our encounter something like "goblin camp". Please make sure to keep your encounter name in lower case.
![image](https://github.com/TheBenjameister/battles-script-generator/assets/82944215/5a5f2826-8379-42e1-8684-97bbb9b45fdc)

Next, lets select goblin from the drop down, and choose how many goblins we want. 
![image](https://github.com/TheBenjameister/battles-script-generator/assets/82944215/06ada795-85a3-4dd9-9ceb-c20c8d10085a)

Now we add a url to an image which we want to use as a token. I chose this one from the forgoten realms wiki : https://www.dndbeyond.com/avatars/thumbnails/30783/955/1000/1000/638062024584880857.png
![image](https://github.com/TheBenjameister/battles-script-generator/assets/82944215/3b1006b4-d1dd-47e5-9c81-f6589ccba64a)

Simply click "Add Monster" to add the monster to your encounter, and you'll see it appear in the table. You can select it at any time and press "Delete Selected Monster" to remove whichever monster you have selected in the table from your encounter. 
![image](https://github.com/TheBenjameister/battles-script-generator/assets/82944215/8f96d9e4-d241-4e80-96e6-501f5673e824)

Now let's repeat the steps with the goblin boss using this image https://www.worldanvil.com/uploads/images/c37fa9a1846f87d869b92ec207f6dec8.jpg :
![image](https://github.com/TheBenjameister/battles-script-generator/assets/82944215/5c01f5db-3daf-49db-a307-704ea08d0e13)

### Step 4
Now that we have our enemies ready to fight, we need a map! Find a map that you like and paste the image url into the box provided. I am using this map from r/battlemaps by EnchantedMaps : https://i.redd.it/67lkuw1dcp961.jpg
![image](https://github.com/TheBenjameister/battles-script-generator/assets/82944215/8c4b898a-4567-407c-b237-1bc61739b447)

Insert the grid size and cell size that you're playing with. This map is designed to be 10x10 with grids that are 45 pixels by 45 pixels. 
![image](https://github.com/TheBenjameister/battles-script-generator/assets/82944215/dc904e1e-b170-49f8-992f-2ec60c5dbf8c)

We are done! Now press generate and we get the following in the terminal (please not that this may take a few moments): 
```json
!uvar Battles {
    "goblin camp": [
        "!init add 20 DM -p",
        "!i effect DM map -attack \"||Size: 10x10 ~ Background: https://i.redd.it/67lkuw1dcp961.jpg ~ Options: c45\"",
        "!i madd Goblin -n 3 -note \"Token: z8hak | Size: S\"",
        "!i madd Goblin Boss -n 1 -note \"Token: gt84v | Size: S\""
    ]
}
```
### Step 5
To use this in discord, simply copy and paste this into your channel 
![image](https://github.com/TheBenjameister/battles-script-generator/assets/82944215/e3eb9203-a54a-482f-9bae-f36a784be6a3)

Then type in `!bplan Battles` to load your battle plan, you should see the following : 
![image](https://github.com/TheBenjameister/battles-script-generator/assets/82944215/0a661572-2e54-4e3d-8ed7-de63ee3dd83a)

Lastly, type in `!bplan begin "Goblin Camp"` and your battle has begun! 
Just move all your tokens to wherever you want them, and you're good to go!

![image](https://github.com/TheBenjameister/battles-script-generator/assets/82944215/83b2b0fa-14de-469b-b871-bc2e481272de)

## Repeated Use
After having loaded a token image once, the token code will be saved in your bestiary. This is what our goblin looks like now:
```json
{
        "name": "Goblin",
        "cr": "1/4",
        "size": "Small",
        "shortcodeToken": "z8hak"
    }
```
And selecting Goblin in the programme disables the token URL box. If you want to delete the code, then you need to manually remove it from the bestiary.

## END
Thank you for using my generator and I hope it has been helpful for you! I will be improving it over time by making it nicer and more user friendly, so check back regularly to see the progress. If you have any bugs to report or suggestions to make, please let me know on discord (you'll find me in the OTFBM server). 

If it has been helpful and you feel like you want to support me, a small tip goes a long way : 

<a href='https://ko-fi.com/thebenjameister' target='_blank'><img height='35' style='border:0px;height:46px;' src='https://az743702.vo.msecnd.net/cdn/kofi3.png?v=0' border='0' alt='Buy Me a Coffee at ko-fi.com' />

