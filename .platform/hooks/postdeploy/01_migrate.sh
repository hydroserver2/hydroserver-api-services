#!/bin/bash

source "$PYTHONPATH/activate" && {

    if [[ $EB_IS_COMMAND_LEADER == "true" ]];
    then
        python manage.py showmigrations;
        python manage.py migrate --noinput;
    else
        echo "Skipping migrations on non-leader node.";
    fi

}