In your ubuntu terminal, type
  ```
  cd ~
  mkdir applications
  ```
#install neo4j
  ```
  mkdir neo4j
  cd neo4j 
  curl -o /tmp/neo4j.tgz http://dev.nanomine.org/neo4j-3.5-and-nm.tgz
  tar zxf /tmp/neo4j.tgz
  ```
#start neo4j with this command
  ```
  ~/applications/neo4j/bin/neo4j start
  ```
  then your neo4j webapp should be running at http://localhost:7474, ask me for the userid and the password.

#download your fork of the nanomine_PDB to applications
  ```
  cd ~/applications
  git clone git@github.com:YOUR_USERNAME/nanomine_PDB.git
  ```
#download xml2neo module at https://github.com/moxious/xml2neo/archive/master.zip

#unzip the file to ~/applications/xml2neo-master and convert xmls to cypher queries
  ```
  cd ~/applications
  find nanomine_PDB/xml/ -name "*.xml" -exec xml2neo-master/xml2neo.py {} \; > neo4jqueries.cypher
  ```
  this might take a while. There will be some error messages during the process, ignore them.

#feed the cypher file to the neo4j-shell
  ```
  cd ~/applications
  cat neo4jqueries.cypher | neo4j/bin/neo4j-shell 
  ```
#wait for the process to end and you are good to go.