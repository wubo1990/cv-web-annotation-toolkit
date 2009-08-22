#!/usr/bin/env python

import os,sys

TE_BIN_LOCATION="/home/syrnick/daria/TreeExtra.1.2/additive_groves/"


def get_next_action(data_root):
    log_fn=os.path.join(data_root,'log.txt');
    log_line=open(log_fn,'r').readlines()[-2].strip();
    if log_line.startswith("Suggested action: "):
        return log_line.replace("Suggested action: ","")
    return None


def make_predictions_with_model(data_root,model_file):

    cmd="%sag_predict -p %s/data.test -r %s/data.attr -m %s -o %s/preds.txt" % (
        TE_BIN_LOCATION,data_root,data_root,model_file,data_root)
    os.system(cmd)
    pass

def build_model(data_root):
    ag_train=os.path.join(TE_BIN_LOCATION,'ag_train')
    
    model_filename=os.path.join(data_root,'model.bin');
    if os.path.exists(model_filename):
        print "Model exists", model_filename
        return

    train_file=os.path.join(data_root,'data.train')
    val_file=os.path.join(data_root,'data.valid')
    test_file=os.path.join(data_root,'data.test')
    attr_file=os.path.join(data_root,'data.attr')

    true_dir=os.getcwd()

    os.chdir(data_root);
    train_cmd = "%s -t %s -v %s -r %s -s slow -n 2" % ( ag_train, train_file, val_file, attr_file )
    print "Next action is ",train_cmd
    train_status = os.system(train_cmd)

    done_training=False
    while not done_training:
        action = get_next_action(data_root)
        print "Next action is ",action
        action_cmd=TE_BIN_LOCATION+action;
        action_status = os.system(action_cmd)        

        if action.startswith('ag_save'):
            done_training=True;

    os.chdir(true_dir);


if __name__=="__main__":
    #print get_next_action('/home/syrnick/daria/TreeExtra.1.2/data/');
    build_model('/home/syrnick/daria/TreeExtra.1.2/data/');
