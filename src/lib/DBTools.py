# -*- coding: utf-8 -*-
import os
import datetime
import MySQLdb
import logging
import sys
from xml.dom.minidom import parse, parseString
from Models import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker, mapper
from sqlalchemy import *
from lib.SQLAlchemyTool import configure_session_for_app, session, _engines

def create_admin_user(dburi, password):
    adminUser = User(id="admin", first_name="Administrator", quota=1024, date_tos_accept=datetime.datetime.now())
    adminUser.set_password(password)
    testUser1 = User(id="wbdavis", first_name="Brett", last_name="Davis", quota=1024, date_tos_accept=datetime.datetime.now())
    testUser1.set_password("test")
    testUser2 = User(id="cmiller", first_name="Chris", last_name="Miller", quota=1024, date_tos_accept=datetime.datetime.now())
    testUser2.set_password("test")
    engine = create_engine(dburi, echo=True)
    #Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    adminPermission = session.query(Permission).filter(Permission.id == "admin").one()
    adminUser.permissions.append(adminPermission)
    oldAdmin = session.query(User).filter(User.id=="admin").scalar()
    if oldAdmin is not None:
        session.delete(oldAdmin)
    session.add(adminUser)
    session.add(testUser1)
    session.add(testUser2)
    session.commit()
    print "Password after set: %s" % str(adminUser.password)

def export_db(exportFile):
    pass
    
def import_db(importFile):
    dom = parse(importFile)

    #Permissions
    for node in dom.getElementsByTagName("Permissions"):
        for permnode in node:
            session.add(Permission(id=permnode.getAttribute("id"), name=permnode.getAttribute("name")))


    #Users
    for node in dom.getElementsByTagName("users"):
        for usernode in node.getElementsByTagName("user"):
            u = User(id=usernode.getAttribute("id"),first_name=usernode.getAttribute(("first_name"),
            last_name=usernode.getAttribute("last_name"), quota=int(usernode.getAttribute("quota")),
            email=usernode.getAttribute("email"), date_last_login=usernode.getAttribute("date_last_login"),
            date_tos_accept=usernode.getAttribute("date_tos_accept")))
            session.add(u)
            session.commit()
            for permnode in usernode.getElementsByTagName("permission")
                perm = session.query(Permission).filter(Permission.id==permnode.getAttribute("id")).one()
                u.permissions.append(perm)
            session.commit()

    #Groups
    #TODO: Add members
    for node in dom.getElementsByTagName("groups"):
        for groupnode in node.getElementsByTagName("group"):
            g = Group(id=groupnode.getAttribute("id"), name=groupnode.getAttribute("name"))
            session.add(g)
            for permnode in groupnode.getElementsByTagName("permissions"):
                perm = session.query(Permission).filter(Permission.id==permnode.getAttribute("id")).one()
                g.permissions.append(perm)
            session.commit()


    #Roles
    #TODO: Add members
    for node in dom.getElementsByTagName("roles"):
        for rolenode in node.getElementsByTagName("role"):
            r = Role(id=rolenode.getAttribute("id"), name=rolenode.getAttribute("name"),
            email=rolenode.getAttribute("email"), quota=int(rolenode.getAttribute("quota")))
            session.add(r)
            for permnode in rolenode.getElementsByTagName("permissions"):
                perm = session.query(Permission).filter(Permission.id==permnode.getAttribute("id")).one()
                r.permissions.append(perm)
            session.commit()
            
    type = Column(Text)
    size = Column(BigInteger)
    notes = Column(Text)
    date_uploaded = Column(DateTime)
    owner_id = Column(String(30), ForeignKey('users.id'), nullable=True)
    role_owner_id = Column(String(30), ForeignKey('roles.id'), nullable=True)
    date_expires = Column(DateTime)
    passed_avscan = Column(Boolean)
    encryption_key = Column(String(64))
    status = Column(String(255))
    notify_on_download = Column(Boolean, nullable=False)
    md5 = Column(String(64), nullable=True)
    upload_request_id = Column(String(64), ForeignKey("upload_requests.id"))
    for node in dom.getElementsByTagName("files"):
        for filenode in node.getElementsByTagName("file"):
            f = File(id=filenode.getAttribute("id"), name=filenode.getAttribute("name"),
                    type=filenode.getAttribute("type"), size=long(filenode.getAttribute("size")),
                    notes=filenode.getAttribute("notes"), date_uploaded=filenode.getAttribute("date_uploaded"),
                    owner_id=filenode.getAttribute("owner_id"), role_owner_id=filenode.getAttribute("role_owner_id"),
                    date_expires=filenode.getAttribute("date_expires"), passed_avscan=filenode.getAttribute("passed_avscan"),,
                    encryption_key=filenode.getAttribute("encryption_key"), status=filenode.getAttribute("status"),
                    notify_on_download=False if filenode.getAttribute("notify_on_download")=="0" else True,
                    md5=filenode.getAttribute("md5"), upload_request_id=filenode.getAttribute("upload_request_id"))
            session.add(f)
        session.commit()








class LegacyDBConverter():
    connection = None
    dbHost = None
    dbUser = None
    dbPassword = None
    dbName = None
    db = None
    cursor = None
    def __init__(self, dbHost, dbUser, dbPassword, dbName, config):
        self.dbHost = dbHost
        self.dbUser = dbUser
        self.dbPassword = dbPassword
        self.dbName = dbName
        self.config = config
        self.get_connection()

    def get_connection(self):
        self.db = MySQLdb.connect(self.dbHost, self.dbUser, self.dbPassword, self.dbName)
        self.cursor = self.db.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    def get_db(self):
        return MySQLdb.connect(self.dbHost, self.dbUser, self.dbPassword, self.dbName)

    def port_database():
        host = raw_input("What is the host of the old DB server?: ")
        db = raw_input("Database: ")
        username = raw_input("Username: ")
        password = getpass("Password: ")
        configParameters = self.GetAllParameters()
        files = self.GetAllFiles()
        groups = self.GetAllGroups ()
        permissions = self.GetAllPermissions()
        userShares = self.GetAllUserShares()
        groupShares = self.GetAllGroupShares()
        hiddenShares = self.GetAllHiddenShares()
        attributes = self.GetAllAttributes()
        attributeShares = self.GetAllAttributeShares()
        publicShares = self.GetAllPublicShares ()
        users = self.GetAllUsers ()
        roles = self.GetRoles()
        messages = self.GetMessages()
        messageShares = self.GetAllMessageShares()
        uploadRequests = self.GetUploadRequests()
        deletedFiles = self.GetAllDeletedFiles()
        auditLogs = self.GetAuditLogs()
        templatePath = os.path.join(self.config['root_path'], "lib", "DataSchema.tmpl")
        tpl = str(Template(file=templatePath, searchList=[locals(),globals()]))
        f = open(os.path.join(os.getcwd(), "FL_Data_Export.xml"), "wb")
        f.write(tpl)
        f.close()
        print "Data has been exported to %s" % templatePath

    def GetAllParameters(self):
        params = []
        sql = "SELECT * FROM config"
        results = self.execute(sql, None)
        if results is not None and len(results)>0:
            for row in results:
                param = ConfigParameter(name=row['config_parameter_name'], description=row['config_parameter_description'], type=row['config_parameter_type'], value=row['config_parameter_value'])
                params.append(param)
        return params

    def GetAllFiles(self):
        sql = "SELECT * FROM file WHERE file_expiration_datetime < now()"
        sql_args = None
        results = self.execute(sql, sql_args)
        allFiles = []
        for row in results:
            currentFile = File(name=row['file_name'], type=row['file_type'], notes=row['file_notes'], size=row['file_size'], date_uploaded=row['file_uploaded_datetime'], owner_id=row['file_owner_id'], date_expires=row['file_expiration_datetime'], passed_avscan=row['file_passed_avscan'], encryption_key=row['file_encryption_key'], id=row['file_id'], status=row['file_status'],  notify_on_download=row['file_notify_on_download'], upload_request_id=row['file_upload_ticket_id'])
            allFiles.append(currentFile)
        return allFiles

#Groups
    def GetAllGroups (self):
        sql = "SELECT * FROM groups"
        sql_args = []
        results = self.execute(sql,sql_args)
        allGroups = []
        for row in results:
            group = Group(id=row['group_id'], name=row['group_name'], owner_id=row['group_owner_id'], scope=row['group_scope'])
            sql_args = [groupId,]
            sql = "SELECT * FROM group_membership WHERE group_membership_group_id=%s"
            memberResults = self.execute(sql,sql_args)
            for memberRow in memberResults:
                groupMembers.append(User(id=memberRow['group_membership_user_id']))
            sql = "SELECT * FROM group_permission WHERE group_permission_group_id=%s"
            permissionResults = self.execute(sql,sql_args)
            for permissionRow in permissionResults:
                group.permissions.append(Permission(id=permissionRow['group_permission_permission_id']))
            allGroups.append(group)
        return allGroups

#Permissions
    def GetAllPermissions(self):
        sql = "SELECT * FROM permission"
        permissions = []
        results = self.execute(sql, None)
        for row in results:
            permissions.append(Permission(id=row['permission_id'], name=row['permission_name']))
        return permissions

#Private Shares
    def GetAllUserShares(self):
        sql = "SELECT * FROM private_share"
        privateShareList = []
        results = self.execute(sql, None)
        for prShR in results:
            privateShareList.append(UserShare(file_id=prShR['private_share_file_id'], user_id=prShR['private_share_target_id']))
        return privateShareList

#Private Group Shares
    def GetAllGroupShares(self):
        sql = "SELECT * FROM private_group_share"
        privateGroupShareList = []
        results = self.execute(sql, None)
        for row in results:
            privateGroupShareList.append(GroupShare(file_idrow['private_group_share_file_id'], group_id=row['private_group_share_target_id']))
        return privateGroupShareList

    def GetAllHiddenShares(self):
        sql = "SELECT * FROM hidden_share"
        results = self.execute(sql, None)
        hidden_shares = []
        for row in results:
            hidden_shares.append(HiddenShare(owner_id=row['hidden_share_target_id'], file_id=row['hidden_share_file_id']))
        return hidden_shares

#Private Attribute Shares
    def GetAllAttributes(self):
        sql = "SELECT * FROM attribute"
        results = self.execute(sql, None)
        attributes = []
        for row in results:
            attr = Attribute(row['attribute_id'], row['attribute_name'])
            attributes.append(attr)
        return attributes

    def GetAllAttributeShares(self):
        sql = "SELECT * FROM private_attribute_share"
        attributeShares = []
        results = self.execute(sql, None)
        for row in results:
            attributeShares.append(AttributeShare(attribute_id=row["private_attribute_share_attribute_id"], file_id=row["private_attribute_share_file_id"]))
        return attributeShares

#Public Shares
    def GetAllPublicShares (self):
        sql = "SELECT * FROM public_share, file WHERE file.file_id = public_share.public_share_file_id"
        results = self.execute(sql, None)
        publicShares = []
        for row in results:
            currentPubShare = PublicShare(id=row['public_share_id'], owner_id=row['file_owner_id'], date_expires=row['public_share_expiration'], password=row['public_share_password_hash'], reuse=row['public_share_type'])
            currentPubShare.files.append(File(id=row['public_share_file_id']))
            publicShares.append(currentPubShare)
        return publicShares

#User functions
    def GetAllUsers (self):
        users = []
        roleUserIds = []
        rSql = "SELECT * FROM permission WHERE permission_id LIKE '(role)%%'"
        sql_args = []
        rolesResults = self.execute(rSql, sql_args)
        for row in rolesResults:
            roleUserIds.append(row['permission_id'][6:])
        
        rolePermissions={}
        pSql = "SELECT * FROM user_permission WHERE user_permission_permission_id LIKE '(role)%%'"
        sql_args = []
        rolesPermResults = self.execute(pSql, sql_args)
        for row in rolesPermResults:
            if rolePermission.has_key(row["user_permission_user_id"])==False:
                rolePermissions[row["user_permission_user_id"]] = []
            rolePermissions[row["user_permission_user_id"]].append(row['user_permission_permission_id'][6:])

        userPermissions={}
        pSql = "SELECT * FROM user_permission WHERE user_permission_permission_id NOT LIKE '(role)%%'"
        sql_args = []
        permResults = self.execute(pSql, sql_args)
        for row in permResults:
            if userPermissions.has_key(row["user_permission_user_id"])==False:
                userPermissions[row["user_permission_user_id"]] = []
            userPermissions[row["user_permission_user_id"]].append(row['user_permission_permission_id'][6:])

        sql = "SELECT * FROM user"
        sql_args = []
        results = self.execute(sql, sql_args)
        currentUser = None
        for row in results:
            if row['user_id'] not in roleUserIds:
                currentUser = User(first_name=row['user_first_name'], last_name=row['user_last_name'], email=row['user_email'], quota=row['user_quota'], date_last_login=row['user_last_login_datetime'], date_tos_accept=row['user_tos_accept_datetime'], id=row['user_id'])
                if (rolePermissions.has_key(currentUser.id)):
                    for roleId in rolePermissions[currentUser.id]:
                        currentUser.roles.append(Role(id=roleId))
                if (userPermissions.has_key(currentUser.id)):
                    for permId in userPermissions[currentUser.id]:
                        currentUser.permissions.append(Permission(id=permId))
                users.append(currentUser)
        return users

    def GetRoles(self):
        rSql = "SELECT * FROM permission WHERE permission_id LIKE '(role)%%'"
        sql_args = []
        roles=[]
        rolesResults = self.execute(rSql, sql_args)
        for row in rolesResults:
            userId = row['permission_id'][6:]
            sql = "SELECT * FROM user WHERE user_id=%s"
            sql_args=[userId,]
            roleUserResults = self.execute(sql, sql_args)
            for userRow in roleUserResults:
                roleName = "%s %s" % (row['user_first_name'], row['user_last_name'])
                roles.append(Role(name=roleName, quota=int(row['user_quota']), email=row['user_email'], id=row['user_id']))
        return roles
    
    def GetMessages(self):
        messages = []
        sql = "SELECT * FROM message"
        results = self.execute(sql, None)
        for row in results:
            messages.append(Message(id=row['message_id'], subject=row['message_subject'], date_sent=row['message_create_datetime'], owner_id=row['message_owner_id'], date_expires=row['message_expiration_datetime'], encryption_key=row['message_encryption_key']))
        return messages

    def GetAllMessageShares(self):
        messageRecipients = []
        sql = "SELECT * FROM message_recipient"
        results = self.execute(sql, None)
        for row in results:
            messageRecipients.append(ReceivedMessage(message_id=row['message_recipient_message_id'], recipient_id=row['message_recipient_user_id'], date_viewed=row['message_recipient_viewed_datetime']))
        return messageRecipients

#Upload Tickets
    def GetUploadRequests(self):
        sql = "SELECT * FROM upload_ticket"
        results = self.execute(sql, None)
        tickets = []
        if results is not None:
            for row in results:
                tickets.append(UploadRequest(owner_id=row['upload_ticket_owner_id'], max_size=row['upload_ticket_max_size'], date_expires=row['upload_ticket_expiration'], password=row['upload_ticket_password_hash'], scan_file=row['upload_ticket_scan_file'], type=row['upload_ticket_type'], id=row['upload_ticket_id']))
        return tickets

    def GetAllDeletedFiles(self):
        sql = "SELECT * FROM deletion_queue"
        sql_args=None
        results = self.execute(sql, sql_args)
        files = []
        for row in results:
            files.append(DeletedFile(file_name=row['deletion_queue_file_path']))
        return files

    def GetAuditLogs(self):
        logs = []
        sql = "SELECT * FROM audit_log"
        results = self.execute(sql, None)
        if results is not None and len(results) > 0:
            for row in results:
                newLog = AuditLog(row['audit_log_initiator_user_id'], row['audit_log_action'], row['audit_log_message'], row['audit_log_action_affected_user_id'], date=row['audit_log_datetime'], id=row['audit_log_id'])
                logs.append(newLog)
        return logs

#CLI Key Management
    def getCLIKeyList(self, userId):
        sql = "SELECT * FROM cli_key WHERE cli_key_user_id=%s"
        sql_args = [userId]
        CLIKeys = []
        results = self.execute(sql, sql_args)
        for row in results:
            newKey = CLIKey(row['cli_key_host_ipv4'], row['cli_key_host_ipv6'], row['cli_key_value'])
            CLIKeys.append(newKey)
        return CLIKeys

    def execute(self, sql, sql_args, getId = False):
        """Executor function, takes arbitrary SQL and argument list, returns all results """
        import warnings
        warnings.simplefilter("ignore")
        try:
            results = None
            if self.cursor is None or self.db is None:
                self.cursor, self.db = (None, None)
                self.get_connection()
                logging.error("Connection was None, rebuilt...")
            try:
                self.cursor.execute(sql, sql_args)
            except MySQLdb.IntegrityError, ie:
                raise ie
            except MySQLdb.OperationalError, oe: #Thread in pool dead maybe, reconnect
                self.cursor, self.db = (None, None)
                self.get_connection()
                self.cursor.execute(sql, sql_args)
            results = self.cursor.fetchall()
            resultId = None
            if getId:
                sql = "SELECT LAST_INSERT_ID() as ID"
                self.cursor.execute(sql, None)
                resultId = self.cursor.fetchone()['ID']
            if getId:
                return results, resultId
            else:
                return results
        except MySQLdb.IntegrityError, ie:
            raise ie
        except Exception, e:
            logging.error("Unable to run SQL query: %s" % str(e))


