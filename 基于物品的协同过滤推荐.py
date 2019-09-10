#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 12:09:04 2019

@author: liujun
"""

import os
import math
import random
import json

class ItCFRec:
    def __init__(self,datafile):
        self.datafile=datafile
        self.data=self.load_data()
        self.train,self.test=self.split_data(3,47)
        self.itemsim=self.item_sim()
        
    def load_data(self):
        print('开始加载数据')
        data=[]
        for line in open(self.datafile):
            userid,itemid,rate,_=line.split("::")
            data.append((userid,itemid,int(rate)))
        return data
    
    def split_data(self,k,seed,m=8):
        print('开始分割数据')
        random.seed(seed)
        train,test={},{}
        for userid,itemid,rate in self.data:
            if random.randint(0,m)==k:
                test.setdefault(userid,{})
                test[userid][itemid]=rate
            else:
                train.setdefault(userid,{})   #userid{itemid:rate}
                train[userid][itemid]=rate
        return train,test
    
    def item_sim(self):
        print('开始计算物品相似度')
        if os.path.exists('item_sim.json'):
            itemsim=json.load(open('item_sim.json','r'))
        else:
            item_user_count=dict()
            count=dict()
            itemsim=dict()
            for userid,items in self.train.items():
                for i in items.keys():
                    item_user_count.setdefault(i,0)
                    if  self.train[userid][i]>0:
                        item_user_count[i]=item_user_count[i]+1
                    for j in items.keys():
                        count.setdefault(i,{}).setdefault(j,0) #{物品1：{物品2,共同评价数}}
                        if self.train[userid][i]>0 and self.train[userid][j]>0 and i!=j:
                            count[i][j]=count[i][j]+1
            for i, related_items in count.items():
                itemsim.setdefault(i,{})
                for j,cuv in related_items.items():
                    itemsim[i].setdefault(j,0)
                    itemsim[i][j]=cuv/math.sqrt(item_user_count[i]*item_user_count[j])
        json.dump(itemsim,open('item_sim.json','w'))
        return itemsim
    
    def recommend(self,user,k=8,nitems=40):
        u_items=self.train.get(user,{})
        resault=dict()
        for i,pi in u_items.items():
            for j,wj in sorted(self.itemsim[i].items(),key=lambda x:x[1],reverse=True)[:k]:
                if j not in u_items:
                    resault.setdefault(j,0)
                    resault[j]=resault[j]+pi*wj
        return dict(sorted(resault.items(),key=lambda x:x[1],reverse=True)[:nitems])
    
    def precision(self,k=8,nitems=10):
        print('开始计算准确率')
        for user in self.test.keys():
            u_items=self.train.get(user,{})
            resault=self.recommend(user,k=k,nitems=nitems)
            hit=0
            sum_nitems=0
            for item, rate in resault.items():
                if item in u_items:
                    hit=hit+1
            sum_nitems=sum_nitems+nitems
            return hit/(sum_nitems*1.0)
                    
    
if __name__=='__main__':
    ib=ItCFRec('ratings.dat')
    result=ib.recommend('1')
    print('user 1 recommend result is {}'.format(result))
    print('准确率为{}'.format(ib.precision()))
                    
                    
    
         
        
                            
                 
                