
if (!db.isMaster()) {
    var msg  = rs.initiate(cfg);
    printjson(msg);
}
