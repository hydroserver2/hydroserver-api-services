#!/bin/bash

source "$PYTHONPATH/activate" && {

    if [[ $EB_IS_COMMAND_LEADER == "true" ]];
    then
        python manage.py configure_timescaledb;
    else
        echo "Skipping timescale configuration on non-leader node.";
    fi

}