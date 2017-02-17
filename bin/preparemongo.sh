#! /bin/bash

cd ../

if [[ $(uname -m) == "x86_64" ]]
then
    wget "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1604-3.2.7.tgz"
    tar -zxf ./mongodb-linux-x86_64-ubuntu1604-3.2.7.tgz --strip-components=1
else
    IFS=" " read -a links <<< $(apt-get -y --print-uris install mongodb | egrep -o "https?://[^']+")
    for link in ${links[@]}
    do
        wget ${link}
    done

    IFS=" " read -a deb_pkgs <<< $(ls ./ | egrep -o "mongo.+\.deb")
    for pkg in ${deb_pkgs[@]}
    do
        dpkg-deb -R ${pkg} ./
    done
fi

