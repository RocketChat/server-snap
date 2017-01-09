var ism = db.isMaster();
if (! (ism.ismaster)) {
    var msg  = rs.initiate();
    printjson(msg);
}
