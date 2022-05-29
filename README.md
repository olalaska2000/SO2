# Multiplayer Bomb Dodger - University project for Operation Systems 2 course
## Authors:
Aleksandra Laska 252696

Izabella Juwa 252786
### Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Example mockup](#example-mockup)
* [Final results](#final-results)
* [Implementation](#implementation)


### General info
The aim of the project is to create an application that uses multithreading and critical sections: mutexes or semaphores.
This project is simple implementation of computer game which consists in discovering individual fields on the board in such a way as not to hit a mine/bomb. Each of each field has a number written directly against it. Game allows participation of more than just one person. The player is initially presented with a grid of undifferentiated squares. Some randomly selected squares, unknown to the player, are designated to contain mines. Typically, the size of the grid and the number of mines are set by the user, by selecting from defined difficulty levels. In each move, the player can choose whether to reveal a particular square (if he / she thinks it is not a mine) or flagging it (if he / she thinks it is a mine).
	
### Technologies
Project is created with:
* Python 
* VSCode/PyCharm environment
* PyGame library
	
### Example mockup
![alt text](https://github.com/Belliee/SO2/blob/readmeFile/GAME.png)

### Final results
* results of minesweeper game for single player
![alt text](https://github.com/olalaska2000/SO2/blob/master/minesweeper.png)



* results of generated board attempting to create multiplayer game on client-server side:
![alt text](https://github.com/olalaska2000/SO2/blob/master/minesweeper2.png)

### Implementation
#### Threads(at least 2 threads)
* thread to listen and display data sent by the server
* thread to wait for a connection from the client

## Why choosing this proect?
It brings memories of one of the first 2000s games as we used to play as kids. It is commonly known and sentimental game we had chance to create and learn new things with the usage of multithreads, semaphore etc.
