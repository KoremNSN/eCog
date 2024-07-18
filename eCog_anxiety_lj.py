'''

'''
### import packages
from glob import glob
import datetime, os, random, time
from psychopy.hardware.labjacks import U3
from psychopy.iohub import launchHubServer # Import port accsess

from psychopy import prefs
prefs.hardware['audioLib'] = ['pygame']

from psychopy import visual, core, event, sound, gui
print(sound.Sound)

# %% Instructions for different tasks in the experiment

sub_cats = ['household', 'heights', 'positive']


overall = ['Thank you for participating in this study!',
           'In this study, you will complete several tasks. The total study will take approximately 40 minutes.'
           'We will explain each task before it begins. Please ask if you have any questions.']

Mundane = ['In the current task, you will listen to a mundane experience.',
           'Please listen attentively, and imagine yourself going through this experience.', 
           'Close your eyes to better picture the event in your mind.']

Positive = ['In the current task, you will listen to a narrative of the positive experience you told us about.',
            'Please listen attentively, and imagine yourself going through this experience.', 
            'Close your eyes to better picture the event in your mind.']

Anxiety = ['In the current task, you will listen to a narrative of the stressful experience you told us about.'
          'Listen attentively and imagine yourself going through this experience.',
          'Close your eyes to better picture the event in your mind.',
          'We understand this may be difficult. You are in a safe environment, and we are here for you if you need anything.']

Picture = ['In the current task, you will passively view images on the screen. Some of these images may be disturbing.',
           'Please focus on the images and how they make you feel.',
           'Look carefully at the images and try to remember characteristic details like unique colors, facial expressions, perspective, lighting, etc.',
           'Loading']

Countdown = ['In the current task, you will have 60 seconds to count backward from 1,000 by 7 as fast as you can.', 'Please begin']

Recall = ['In the previous task, you saw images from 3 categories. In the current task, you have 2.5 minutes per category to remember as many pictures as you can.',
          'Describe at least 3 unique features of each picture to ensure accuracy.']

Auditory = ['In the current task, you will listen to sounds. Some may be disturbing.',
            'Focus on the sounds and how they make you feel.']

# %% Create a subject class to encapsulate subject-specific data and methods
class subject:
    
    def __init__(self, sub_n):
        self.subjectID = sub_n # get subject number
    
        # create a window object
        self.win = visual.Window(color=[0,0,0], screen = 1, fullscr=True)
        
        # create a time stamp at the begining of the run
        date=datetime.datetime.now()
        self.time_stamp = str(date.day) + str(date.month) + str(date.year) + str(date.hour) + str(date.minute) + str(date.second)
        
        # Create files and folders for the run
        self.cwd = os.getcwd()
        timingfile = self.cwd + '\\data\\eCogT_' + str(self.subjectID) + '_' + str(self.time_stamp)
        ratingfile = self.cwd + '\\data\\eCogR_' + str(self.subjectID) + '_' + str(self.time_stamp)
        audiogfile = self.cwd + '\\data\\eCogA_' + str(self.subjectID) + '_' + str(self.time_stamp)
        
        if not os.path.isdir('data\\'):
           os.makedirs('data\\')
        self.dataFile = open(timingfile+'.csv', 'w')
        self.ratingFile = open(ratingfile+'.csv', 'w')
        self.audioFile = open(audiogfile+'.csv', 'w')
        
        # Write headers for the output files
        self.dataFile.write('Sub,time,Trial_n,category,img,FixationOnset,StimulusOnset\n')
        self.ratingFile.write('Sub,category,img,rating,RT\n')
        self.audioFile.write('Sub,time,Trial_n,category,sound,SoundOnset\n')

        self.mouse = event.Mouse()
        self.lj = U3() # open port for LabJack
        self.lj.setFIOState(0,0)
        
        # Create objects for the experiment
        self.fixation = visual.Circle(self.win, radius=10, fillColor='black',lineColor='black',units = 'pix')
        self.sound = sound.Sound('Sounds\\Soundtest.wav', sampleRate=48000,  stereo=True)
        self.pic = visual.ImageStim(self.win, pos=(0,0))
        self.Text = visual.TextStim(self.win, text="US", pos=(0,0), font='Courier New',
                                    anchorVert = 'center', anchorHoriz = 'center', color = 'black',
                                    units = 'norm')
        self.picrating = visual.RatingScale(self.win, scale = '', stretch = 2, showAccept = False, labels = ['Unpleasant', 'Pleasant'],
                                        low = 1, high=  100, tickHeight = 0, singleClick = True) # VAS
        self.trial_n = 0

# %% Method to display text instructions

    def text_display(self, texts = [], tme = 0, consecutive = False):
        for msg in texts:
            self.lj.setFIOState(0,0)
            self.Text.text = msg
            self.Text.draw()
            self.win.flip()
            if tme >0:
                self.lj.setFIOState(0,1)
                time.sleep(tme)
                self.lj.setFIOState(0,0)
            else:
                event.waitKeys(keyList = ['7'])
            if consecutive == True:
                self.Text.text = "done"
                self.Text.draw()
                self.win.flip()
                event.waitKeys(keyList = ['7'])

# %% Method to play the scripted text (mandane and trauma)    
    def script(self, msg = 'Get ready', sound_file = 'Soundtest.wav'):
            
        event.clearEvents()
        self.sound = sound.Sound('Sounds\\scripts\\' + sound_file + '.wav')
        self.Text.text = msg
        self.Text.draw()
        self.win.flip()
        self.lj.setFIOState(0,0)
        event.waitKeys(keyList = ['7'])        
        
        while True:
            self.sound.play()
            self.lj.setFIOState(0,1)
            self.fixation.draw()
            self.win.flip()
            buttonPress=event.waitKeys(keyList = ['7','8'])
            self.lj.setFIOState(0,0)
                 
            if buttonPress == ['8']:
                break           


# %% Methods for the Recall Experiment
            
    # create ITI list
    def create_range(self, start, end, num_items):
        if num_items < 2:
            raise ValueError("num_items must be at least 2 to create a range.")
        step = (end - start) / (num_items - 1)
        return [start + step * i for i in range(num_items)]

            
    # Method to set up the sequence of images for the experiment
    def seq_order(self, picpercat=12, reps = 4):
        
        # Collect all images           
        self.DisturbingRelated       = glob('Images\\DisturbingRelated\\*.png')
        self.Positive                = glob('Images\\Positive\\*.jpg')
        self.neutral                 = glob('Images\\neutral\\*.jpg')
                
        # Make sure no more than picpercat pictures are in the list
        self.DisturbingRelated       = self.DisturbingRelated[:picpercat]
        self.Positive                = self.Positive[:picpercat]
        self.neutral                 = self.neutral[:picpercat]
        
        # Unite images to a single list
        self.img = self.DisturbingRelated + self.Positive + self.neutral
        
        # How many repetions of each image
        self.images = []
        for rep in range(reps):
            random.shuffle(self.img)
            self.images = self.images + self.img
        # self.images = self.img*reps
        self.iti = self.create_range(.5, 1, reps)*picpercat*3
        random.shuffle(self.iti)
  
        
        self.piclist = [] # need to start with an empty list

        # Preload imagess, create an image stimulus from each file, and store in the list:
        for file in self.images:
            self.piclist.append(visual.ImageStim(win=self.win, image=file))       
        
    # Method to run a the visual reimnder experiment
    def trial(self):
        
        self.text_display(['Get ready'])
        
        # Start a clock
        clock = core.Clock()
        
        # Run the experiment
        for i in range(len(self.piclist)):
            # each trial start with a fixation
            self.lj.setFIOState(0,0)
            self.fixation.draw()
            # Get fixation onset time
            fixStart = clock.getTime()
            self.win.flip()
            # Fixation time is 500 ms + a random ITI generated earlier to prevent CNV.
            time.sleep(.5+self.iti[i])
            # Draw image
            self.piclist.pop().draw()
            # Get image onset time
            stimStart = clock.getTime()
            self.lj.setFIOState(0,1)
            self.win.flip()
            # image displyed for 1500 ms
            time.sleep(1.5)
            
            
            # Get the name of the category and image
            category, img = self.images[i].split('\\')[-2:]
            # Write times to file
            self.dataFile.write('{0},{1},{2},{3},{4},{5},{6}\n'.format(self.subjectID,self.time_stamp,self.trial_n,category,img,fixStart,stimStart))
            self.trial_n += 1
            
    # Method to rate image valence
    def pic_rating(self):
        # Display image in random order
        random.shuffle(self.img)
        # Set the text location on the upper portion of the screen
        self.Text.pos = (0,.5)
        self.Text.text = 'Please rate this image valance'
        
        
        for img in self.img:
            self.pic.image=img
            self.picrating.reset()
            # White for mouse response
            while self.picrating.noResponse:
                self.pic.draw()
                self.Text.draw()
                self.picrating.draw()
                self.win.flip()
            
            # Write data to file
            imgrating, ratingRT = self.picrating.getRating(), self.picrating.getRT()
            category, pic = img.split('\\')[-2:]
            self.ratingFile.write('{0},{1},{2},{3},{4}\n'.format(self.subjectID,category,pic,imgrating,ratingRT))

    # Method for picture recall task sequence
    def Pic_recall(self , cats = sub_cats):
        # Orgnize images
        self.seq_order()
        # Run 1st part
        self.trial()
        # Run distractor task
        self.text_display(Countdown)
        time.sleep(60)
        # Run the recall portion of the task
        random.shuffle(cats)
        blocks = ['Recall pictures from the category related to ' + cats[0], 'Recall pictures from the category related to ' + cats[1], 'Recall pictures from the category related to '  + cats[2]]
        # Display instractions
        self.text_display(Recall)
        self.lj.setFIOState(0,0)
        # display the blocks
        self.text_display(blocks, 150, True)
        self.lj.setFIOState(0,1)
        self.win.flip()
        self.dataFile.write(str(cats))
            
        # Run the picture rating task
        self.pic_rating()
            
# %% Method to play audio reminders
    def audio_reminders(self):
        
        # Get audio clips        
        Neutral_audio = glob('Sounds\\Neutral\\*.wav')
        Trauma_audio  = glob('Sounds\\Trauma\\*.wav')
        Positive_audio  = glob('Sounds\\Positive\\*.wav')
        
        # Combine to 1 list
        sounds = Neutral_audio + Trauma_audio + Positive_audio
        
        # shuffle list
        random.shuffle(sounds)
        
        self.soundlist = []
        
        for file in sounds:
            self.soundlist.append(sound.Sound(file))
            
        trial_n = 0
        
        # Get inital time
        clock = core.Clock()
        
        for s in self.soundlist:
            # preload the sound
            #self.sound = sound.Sound(s)
            self.fixation.draw()
            self.lj.setFIOState(0,0)
            # get fixation onset
            fixStart = clock.getTime()
            self.win.flip()
            time.sleep(.5)
            # get sound ouset
            stimStart = clock.getTime()
            #self.sound.play()
            self.lj.setFIOState(0,1)
            s.play()
            # play sound
            time.sleep(1.5)
            self.win.flip()
            category, audio = sounds[trial_n].split('\\')[-2:]
            trial_n += 1
            
            # write data
            self.audioFile.write('{0},{1},{2},{3},{4},{5}\n'.format(self.subjectID,trial_n,category,audio,fixStart,stimStart))
            
        
# %% Method to end the experiment 
    def exp_end(self):
        event.globalKeys.remove(key='q',modifiers = ['ctrl'])
        event.clearEvents() 
        self.lj.close()
        self.win.close()
        core.quit()
        
# %% menu

    def menu(self):
        buttonPress = '0'
        while buttonPress != '6':
            self.Text.pos = (0,0)
            self.Text.text = " 1. Script neutral .\n 2. Script negative .\n 3. Script positive .\n 4. Visual task     .\n 5. Auditory task   .\n 6. End exp         ."
            self.Text.draw()
            self.win.flip()
            buttonPress = event.waitKeys(keyList = ['1','2','3','4','5','6'])
            if buttonPress == ['1']:
                self.text_display(Mundane) # Display mundane script instructions
                self.script(sound_file = 'mandane') # Run mundane script
            elif buttonPress == ['2']:
                self.text_display(Anxiety) # Display trauma script instructions
                self.script(sound_file = 'anxiety') # Run trauma script
            elif buttonPress == ['3']:
                self.text_display(Positive) # Display trauma script instructions
                self.script(sound_file = 'positive')
            elif buttonPress == ['4']:
                self.text_display(Picture) # Display recall task instructions
                self.Pic_recall()  # Run picture recall task
            elif buttonPress == ['5']:
                self.text_display(Auditory)  # Display auditory task instructions
                self.audio_reminders()  # Run auditory reminders task
            else:
                self.text_display(['Thanks for your participation'])  # Display end of experiment message
                self.exp_end()  # End the experiment

# %% Main function to run the experiment
def main():        
    event.globalKeys.add(key='q',modifiers = ['ctrl'], func = core.quit)
    expInfo = {'subject no':''}
    gui.DlgFromDict(expInfo, title='The origin of memories', fixed=['dateStr'])
    sub = subject(expInfo['subject no']) # Create a subject
    sub.text_display(overall) # Display overall instructions
    sub.menu()
    
    

# Run the main function if this script is executed
if __name__ == '__main__':
    main()