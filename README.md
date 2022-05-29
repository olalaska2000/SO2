# Multiplayer Bomb Dodger - University project for Operation Systems 2 course
## Authors:
Aleksandra Laska 252696

Izabella Juwa 252786
### Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Example mockup](#example-mockup)
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
![alt text](https://github.com/olalaska2000/SO2/blob/master/minesweeper.png)




![alt text](https://github.com/olalaska2000/SO2/blob/master/minesweeper2.png)

### Implementation
#### Threads(at least 2 threads)
* thread to listen and display data sent by the server
* thread to wait for a connection from the client
