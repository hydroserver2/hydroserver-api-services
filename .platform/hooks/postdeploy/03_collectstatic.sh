#!/bin/bash

source "$PYTHONPATH/activate" && {

    if [[ $EB_IS_COMMAND_LEADER == "true" ]];
    then
        python manage.py collectstatic --noinput;
    else
        echo "Skipping static collection on non-leader node.";
    fi

}