# II Project

This project is based on python, codesys and postgresql, and runs on Windows 10.

After installing python3.8, create a virtual environment using the commands  
`python -m virtualenv venv`
`.\venv\Scripts\activate`

**Note**: Powershell should allow to run scripts to perform the previous commands. If that happens, follow this [link](https://stackoverflow.com/questions/4037939/powershell-says-execution-of-scripts-is-disabled-on-this-system).  

After setting up the virtual environment run the file requirements.txt  
`python -m pip install -r requirements.txt`

## Setting up the MES

It is possible to change the MES to interact with the PLC, the database and the UDP as long as they all share the same network. Under the file directory, the `config.json` should be changed with the IP of the machine running the respective service.  

**Note**: All the arguments should be written surrounded by double quotation marks ("")

## Running the program

Run the following command in the virtual environment's terminal on the source directory:  
`python .\Main.py`

## Terminate the program

Select the terminal running the MES and press `Ctrl`+`Fn`+`b` or `Ctrl`+`Break`

## Configuring the database

In order to install docker on windows please download the latest docker toolbox .exe release from [the official repo](https://github.com/docker/toolbox/releases).

**Notes**: You need to have Intel VT-x or AMD-V hardware virtualization enabled or the instalation will fail. If this happens, please enable it in your computers's BIOS and retry.

### Installing Docker

1.  Run the installer using the full instalation configuration and remember to tick the option to install VirtualBox.
2.  Run the Docker Quickstart Terminal shortcut and wait for the setup to finish.

### Setting up the database

1.	Open the Docker Quickstart Terminal or whichever shell you prefer (admin access may be needed)
2.	Navigate to the /II_project/db directory
3.	Run: `docker-compose up -d`
4.	After the containers are created you can check on them using: `docker ps`

### Remote access the database 

1.	Oracle VM VirtualBox should be installed by default after installing docker. Run the application
2.	Open the settigns and navigate to the Network tab
3.	Open Port Forwading under the Advanced options
4.	Create 2 new rules like the following  
		`Name: pqadmin, Host Port: 5050, Guest Port: 5050`  
		`Name: postgres, Host Port: 5432, Guest Port: 5432`

### Accessing the database through PgAdmin

You can now access the PgAdmin webpage by going to your prefered browser and entering the following adress:  

`<YOUR-DOCKER-MACHINE-IP>:5050`  

Where your `<YOUR-DOCKER-MACHINE-IP>` is usually by default `192.168.99.100` if not, you can check it by running `docker-machine ip` on the shell.

#### Credentials
##### pgadmin
**User:** ii@project.com  
**Password:** ii_project  

##### database  
**User:** ii  
**Password:** ii_project

### Removing the database

To delete all containers and data run:

`docker-compose down --volumes` or `docker-compose down -v`
