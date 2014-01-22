# Prerequirements

- python2 
- python2-virtualenv
- all the python bonus modules from Requirements.txt

## Ubuntu

    apt-get install python python-virtualenv

# Install

  cd /opt
  git clone <this-repo> musical_cleansing
  cd musical_cleansing
  virtualenv .
  pip install -r Requirements.txt

# Autostarting
    
    # add the following to /etc/rc.local
    tmux new-session -s root -d '/opt/musical_cleansing/start_button.sh'
    tmux new-window -t root:1 '/opt/musical_cleansing/start_hal.sh'
