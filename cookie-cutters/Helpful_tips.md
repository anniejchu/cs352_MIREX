# (Potentially) Helpful Tips from PM (EJ)

## Improving over Baselines
If your team's goal is getting better evaluation metrics than the baseline implementations for either chord analysis or beat tracking, we don't want you to become overwhelmed with a sea of research papers when looking for inspiration. Many contemporary methods will have specific parameters, training setups, pipelines, etc, that might be hard to navigate at first, _especially_ if you're not comfortable with digesting research papers or specific deep learning concepts. 

For that reason, a good place to start is by thinking about what we've learned in class and the assignments. For either the chord or beat tracking implementations, think about what might make them weak or fragile, either from an assumption the solutions make to a lack of expressivity in the pipeline.

For example, if we made a baseline implementation for sound source separation using the same principles as REPET, one thing you would be wise to remember from that topic was that REPET is intrinsically dependent on repetition in the audio and that the pipeline for separating audio is entirely algorithmic. What happens when this assumption breaks and our hard-coded system becomes fragile to unique data? This is something many of you noticed in the reflection of this assignment, and rightfully so. 

One avenue this might make you explore is finding a system or model that can _learn_ what musical stems sound like and extracting them rather than assuming what they are from repetition. Thankfully, our most recent homework had you dive into deep learning models, various training tasks (supervised vs contrastive), and analyzing how data affects what your model can learn.

Applying this 'investigative' approach to the baselines we gave you might make it easier to (1) understand how existing methods do it and (2) give you a more concrete starting place to explore from.

## Choosing and Using Datasets
We are giving you a lot of freedom in what datasets you want to use for this, so be curious and search around. With that said, HW4 showed that what your data is, particularly when using deep learning, makes or breaks your system. With that in mind, I strongly suggest you do these things when finding a dataset:
1. **READ** the documentation. Where is it from? How was it made? What does it contain? You should not be blindly throwing data into your system.
2. **How compatible is it** with your system and other datasets? If you have 8 datasets all from a different source, you will have a lot of diversity which tends to lead to better results. A common issue is how you process that data. Is everything the same sample rate? Is one set quieter than the others? Be inquisitive about what you use and how it might affect your results, and manual inspection/listenting can be great to avoid glaring issues.
3. **Try to source it ethically.** Not much else to be said on this one, but there are plenty of free to use (usually with crediting the creator) sets online

## Avoiding Silly Mistakes
There are a few places I can see silly mistakes come up that could affect the performance of your model or have it crash. Just watch out for these.

1. Fixed sample rate (or other variable) for processing data without checking it works with the file.
2. Off by one errors. This is especially important for beat tracking.
3. Hard-coded variables. If you always expect your audio to be at least 10 seconds in length and a new file comes in that is less than that, make sure your system is either robust to handle it or you preprocess data and handle it some other way.


## Reaching Out to Us
If you have questions, we are always happy to help. Our research is quite literally this, so we can always guide you if you're having issues or questions. My (EJ's) office hours are Wed. 2PM-3PM and my schedule is more light now, so I can dedicate more time if need be.

