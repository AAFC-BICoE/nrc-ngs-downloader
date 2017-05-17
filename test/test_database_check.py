from ConfigParser import SafeConfigParser
import sys
sys.path.append('/home/zhengc/NRC-LIMS-dataDownloader')
from nrc_ngs_dl import lims_database.LimsDatabase
from nrc_ngs_dl import web_parser.WebParser

    
def main():
    config_parser = SafeConfigParser()
    config_parser.read('/home/zhengc/NRC-LIMS-dataDownloader/config.ini.sample')
    DB_NAME = config_parser.get('sqlite_database', 'name')
    USERNAME = config_parser.get('nrc_lims','username')
    PASSWORD = config_parser.get('nrc_lims','password')
    LOGIN_URL = config_parser.get('nrc_lims','login_url')
    RUNLIST_URL = config_parser.get('nrc_lims','runlist_url')
    #DESTINATION_FOLDER = config_parser.get('output','path')
    
    #connect to database if the database exist
    #otherwise create tables for this database
    lims_database = LimsDatabase(DB_NAME)
    print("before delete")
    lims_database.check_dp_table()
    #modify database
    print('after delete')
    #lims_database.delete_last_run()
    lims_database.modify_http_header(9, '1876989409')
    lims_database.delete_a_run(2)
    lims_database.check_dp_table()
    
    #login to LIMS webpage   
    web_parser = web_parser(LOGIN_URL,RUNLIST_URL,USERNAME,PASSWORD)
    #get all the information of completed packages
    #url_for_the_run, run_name, plate_name, Plateform, Operator, Creation Date, Description, status
    run_list = web_parser.get_runlist()
    #check against database, get a list of new packages that haven't been downloaded
    #need to modified for reprocessed data
    #new_run_list = lims_database.check_new_run_list(run_list)
    for a_run in run_list:
        run_url = a_run[0]
        run_info = web_parser.get_runinfo(run_url)
        lane_info = web_parser.get_laneinfo(run_url)
        for a_lane in lane_info:
            case = lims_database.check_new_run(run_info,a_lane)
            if case == 2:
                print("new sequence run:", a_lane)
                file_info = web_parser.get_fileinfo(run_url,a_lane)
                rowid = lims_database.insert_run_info(run_info)
                lims_database.insert_lane_info(rowid,run_url,a_lane)
                lims_database.insert_file_info(rowid,file_info)
            if case ==3:
                print("re-processed sequence run:", a_lane)
                #file_info = web_parser.get_fileinfo(run_url,a_lane)
                #rowid = lims_database.insert_run_info(run_info)
                #lims_database.insert_lane_info(rowid,run_url,a_lane)
                #lims_database.insert_file_info(rowid,file_info)
            if case == 1:
                print('old data', a_lane)
                
    lims_database.check_dp_table()
    lims_database.check_df_table()
    lims_database.disconnect()
    
    
if __name__ == '__main__':
    main()

