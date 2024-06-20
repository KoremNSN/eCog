### import packages
from glob import glob
import datetime, os, random, time
from psychopy import visual, core, monitors, event, sound

# %% create a subject object
class subject:
    
    def __init__(self, sub_n):
        self.subjectID = sub_n # get subject number
    
        # create a window object
        self.win = visual.Window(color=[0,0,0], screen = 1, fullscr=True)
        
        # create a time stamp at the begining of the run
        date=datetime.datetime.now()
        self.time_stamp = str(date.day) + str(date.month) + str(date.year) + str(date.hour) + str(date.minute) + str(date.second)
        
        # create file and folder for the run
        self.cwd = os.getcwd()
        fileName = self.cwd + '/data/eCog_' + str(self.subjectID) + '_' + str(self.time_stamp)
        if not os.path.isdir('data/'):
           os.makedirs('data/')
        self.dataFile = open(fileName+'.csv', 'w')
        
        #writes headers for the output file
        self.dataFile.write('Sub,time,Trial_n,category,img,FixationOnset,StimulusOnset\n')

        
        
    
        # creates the visual objects for the experiment
        self.fixation = visual.Circle(self.win, radius=10, fillColor='black',lineColor='black',units = 'pix')
        self.sound = sound.Sound('Soundtest.wav')
        self.pic = visual.ImageStim(self.win, pos=(0,0))
        self.Text = visual.TextStim(self.win, text="US", pos=(0,0), font='Courier New',
                                    anchorVert = 'center', anchorHoriz = 'center', color = 'black',
                                    units = 'norm')
        self.trial_n = 0
    
    def script(self, msg = 'please relax', sound_file = 'Soundtest.wav'):
            
        event.clearEvents()
        self.sound = sound.Sound(sound_file)
        self.Text.text = msg
        self.Text.draw()
        self.win.flip()
        event.waitKeys(keyList = ['5'])        
        
        while True:
            self.sound.play()
            self.fixation.draw()
            self.win.flip()
            buttonPress=event.waitKeys(keyList = ['7','8'])
                 
            if buttonPress == ['8']:
                break           
    
    def seq_order(self, picpercat=12):
        
        # Collect all images           
        self.DisturbingRelated       = glob('images/DisturbingRelated/*.png')
        self.DisturbingUnrelated     = glob('images/DisturbingUnrelated/*.png')
        self.neutral                 = glob('images/neutral/*.jpg')
                
        self.DisturbingRelated       = self.DisturbingRelated[:picpercat]
        self.DisturbingUnrelated     = self.DisturbingUnrelated[:picpercat]
        self.neutral                 = self.neutral[:picpercat]
        
        self.img = self.DisturbingRelated + self.DisturbingUnrelated + self.neutral
        
        self.images = self.img*2
        self.iti = [.5, .6]*picpercat*3
        random.shuffle(self.iti)
        
        self.piclist = [] # need to start with an empty list

        # create an image stimulus from each file, and store in the list:
        for file in self.images:
            self.piclist.append(visual.ImageStim(win=self.win, image=file))
        test =''
        while True:
            random.shuffle(self.piclist)
            for pic in self.piclist:
                if pic == test:
                    continue
                else:
                    test = pic
            break
        
            
    def trial(self):
        
        clock = core.Clock()
        
        for i in range(len(self.piclist)):
            self.fixation.draw()
            fixStart = clock.getTime()
            self.win.flip()
            time.sleep(.5)
            self.piclist.pop().draw()
            stimStart = clock.getTime()
            self.win.flip()
            time.sleep(1.5)
            self.win.flip()
            time.sleep(self.iti[i])
            
            
            category, img = self.images[i].split('/')[-2:]
            self.dataFile.write('{0},{1},{2},{3},{4},{5},{6}\n'.format(self.subjectID,self.time_stamp,self.trial_n,category,img,fixStart,stimStart))
            self.trial_n += 1
            
    def text_display(self, msg, time):
        self.Text.text = msg
        self.Text.draw()
        self.win.flip()
        time.sleep(time)
        
    def pic_rating(self):
        random.shuffle(self.img)
        
        #for img in self.img:
            # get rating from subtyping
        
    def Pic_recall(self):
        self.seq_order()
        self.trial()
        self.text_display("please count backword from 1000 by 7", 60)
        blocks = ['Neutral', 'trauma-related', 'trauma-unrelated']
        random.shuffle(blocks)
        for block in blocks:
            self.text_display(block, 150)
            self.win.flip()
            self.dataFile.write(block)
            event.waitKeys(keyList = ['5'])
        
    
    def exp_end(self):
        event.clearEvents() 
        self.win.close()
        core.quit()

def main():        
    event.globalKeys.add(key='q',modifiers = ['ctrl'], func = core.quit)
    sub = subject(1)
    #sub.script('mandane')
    #sub.script('trauma')
    sub.Pic_recall()
    sub.exp_end()
    


if __name__ == '__main__':
    main()