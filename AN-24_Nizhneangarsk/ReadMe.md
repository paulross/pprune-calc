# AN-24 Accident at Nizhneangarsk, Russia

On Thursday 27 June 2019 an AN-24 of Angara Airlines, flight number 2G-200, flying from Ulan-Ude Airport was destroyed whilst landing at Nizhneangarsk Airport. Reportedly, the left engine had failed in flight.

A video of the landing was posted online apparently taken by a passenger sitting on the right hand side under the wing (this record is called here video 'A').
A second video (video 'B') emerged that was taken from a fixed security camera overlooking the airfield.
In both videos the aircraft approaches at high speed and after touchdown it veers off the runway to the right eventually colliding with a series of obstructions. 

This is an analysis of these videos that gives a picture of the speed, position and acceleration forces experienced by the aircraft.



## Summary of Observations

Times are video 'A' unless stated otherwise.

* At the start of the video A the aircraft is on the extended centreline of Nizhneangarsk runway 23 (length 1653 m) at a distance of 2482±98 m from the start of the runway. Ground speed is 82.8±2.0 m/s, (161±4 knots).
* The ground speed slowly increases to a maximum of 92.7±3.5 m/s (180±7 knots) at around t=17.0 seconds when the aircraft is 964±44 m from runway 23.
* The aircraft crosses the start of runway 23 at t=27.5 travelling at 88.6±2 m/s (172±4 knots).
* Touchdown is at t=33.8 s, 549±14 m from the runway start (about 1/3rd of the way down) at 84.3±2 m/s (164±4 knots). Acceleration is -1.1 m/s^2 .
* At t=36.0 the aircraft starts drifting to the right, possibly due to a burst tyre. The aircraft is 731±16 m down the runway travelling at 81.8±2 m/s (159±4 knots).
* The aircraft departs the runway at t=46.1 s, 1463±41 m down the runway at 58.7±3.0 m/s (114±6 knots). Acceleration is -3.9 m/s^2 .
* At t=56.1 there is an impact with the boundary fence 1853m from the start of the runway. This collapses the starboard undercarriage (and probably the port one as well). Impact speed is around 19 m/s (37 knots). 
* The aircraft would have slid to a stop roughly 45m later unfortunately there was a building 36m from the boundary fence which is the site of the final impact. Time is about t=58.0 and speed is somewhat less than 9 m/s (18 knots).

The annotated image below shows the estimated ground path of the aircraft in dotted red with significant events in yellow:

<center>
<img src="img/GoogleEarth_C_Annotated.png" />
</center>

## Resources

Apart from the videos, there is:

* Wikipedia on [Angara Airlines Flight 200](https://en.wikipedia.org/wiki/Angara_Airlines_Flight_200) and on [Nizhneangarsk Airport](https://en.wikipedia.org/wiki/Nizhneangarsk_Airport)
* [AV Herald](http://avherald.com/h?article=4c9b1ac2&opt=0)
* [Aviation Safety Network](https://aviation-safety.net/database/record.php?id=20190627-0)
* Videos from [RT](https://www.rt.com/news/462775-russia-nizhneangarsk-crash-landing/)
* Hi resolution (~0.6m per pixel) imagery of the area, for example from [google maps](https://www.google.com/maps/@55.8088004,109.6072157,835m/data=!3m1!1e3).


# Data From Video A

Video A [https://youtu.be/LtJcgdU5MUk](https://youtu.be/LtJcgdU5MUk) is taken from inside the aircraft.

<center>

[![AN-24 at Nizhneangarsk](https://img.youtube.com/vi/LtJcgdU5MUk/0.jpg)](https://youtu.be/LtJcgdU5MUk "AN-24 at Nizhneangarsk")

</center>

The following techniques are used to calculate the position of the aircraft during this video:

* Matching landmarks in the video with aerial imagery.
* Examining runway details in the video to estimate the aircrafts ground speed.
* Calculating the likely progress of a ballistic body.

Video metadata shows the video was shot at 30 frames per second.

## Landmarks in the Video

The video shows some distinct landmarks, in particular some colourful and readily identifiable buildings which can be seen on aerial imagery. These are used to find the aircraft position on the extended centreline of runway 23 (the aircraft appears to make a straight in approach with little lateral deviation).

Here are two examples.
Frame 1 (t=0s) shows the line up of the edge of a settlement with a dark smudge on a sandy part of an island.
The magenta line shows the estimated ground line the aircraft is flying across, the red line is the extended centreline of runway 23:

<center>

| Camera View | Aerial View |
| :--: | :--: |
| <img src="img/frame0001.jpg" width="140" /> | <img src="img/frame0001_map.png" width="400" /> |

</center>

This puts the aircraft 2490±98m from the start of runway 23.

The second example is frame 483 (t=16.0s) where a two distinctive buildings are lined up:

<center>

| Camera View | Aerial View |
| :--: | :--: |
| <img src="img/frame0483.png" width="140" /> | <img src="img/frame0483_map.png" width="400" /> |

</center>

This puts the aircraft at 1041 ±49m from the start of runway 23.

There are numerous opportunities here but around 15 measurements are sufficient to establish the flight path. This measurement is of distance and this can be differentiated to give velocity. Errors in this method is estimated to be ±100m when 2500m from the runway, reducing to ±10m at the runway edge.

This technique is useful but it requires identifiable ground features and few exist after the aircraft crosses the threshold, and none once 330m beyond the start of runway 23 (the runway markings are useful). Fortunately another technique exists due to the particular construction of this runway which is typical of Siberian airports. Even better, these two (independent) techniques overlap for about four seconds so that the analysis can be cross checked.


## Counting Slabs

The runway at Nizhneangarsk is made of concrete slabs that are ubiquitous in Siberia for roads and airfields. This gives the runway a particular pattern where vegetation or water staining at the slab edges contrasts with the pale concrete of the slab.
These edges can be clearly seen, and measured, on the video and high-resolution aerial imagery.
The aircraft's progress across these slabs can be used to calculate the velocity. This can be integrated for distance or differentiated for acceleration.

### Standard Slabs

Standardised slabs used for roads and runways in Siberia measure 6m x 1.8m (data from the author's engineering file). For confirmation here is an enhanced aerial image of the runway at Nizhneangarsk where the south side of the runway has been annotated, rather crudely, with yellow lines at the edge of each slab (the slabs are laid with their long side in the runway direction).

<center>
<img src="img/RunwaySlabs.png" width="200" />
</center>

Measurement of this imagery shows that these 10 slabs are 98 pixels long which, at 0.617 m/pixel for this image, gives a slab length of 6.05m. The value of 6m for slab length is used hereon.

### Speed by Slab Transits

These slab edges can be seen quite clearly on video 'A', as an example here are two frames [841 and 843] which are 1/15 second apart (at 30 fps). On the left are the original frames, on the right the edges of the slabs are identified with yellow lines.

<center>

| Original Frames | Showing slab edges |
| :--: | :--: |
| <img src="img/frame0841.jpg" width="120" />&nbsp;<img src="img/frame0843.jpg" width="120" /> | <img src="img/frame0841_annotated.png" width="120" />&nbsp;<img src="img/frame0843_annotated.png" width="120" /> |
</center>

The broad yellow line on the first image is the same part of the runway as the broad line on the second image. The near match of the right hand line in the first frame with the line in the second frame indicates that the aircraft has traveled almost exactly 6m in that 1/15th second. The light patch on the right of the concrete, and the lightish patch in the grass confirms this sequence.

This gives a ground speed of 90 m/s (175 knots). The error term is how confident the slab match is, in general this assumed to be 10% of a slab, so 0.6m in this example thus ±9 m/s (±18 knots). If a succession of slabs can be counted the error is proportionally reduced. This is a speed measurement and can be integrated for distance or differentiated for acceleration.


# Data From Video B

A second video [https://youtu.be/BQ8ujmRhLH0](https://youtu.be/BQ8ujmRhLH0) was posted on YouTube that showed images from a security camera overlooking the airport, here referred to as video 'B'. The camera is facing roughly south west and was recorded at 25 frames per second.

<center>

[![AN-24 at Nizhneangarsk, video B](https://img.youtube.com/vi/BQ8ujmRhLH0/0.jpg)](https://youtu.be/BQ8ujmRhLH0 "AN-24 at Nizhneangarsk, video B")

</center>

## Camera Position

The distinctive foreground means the camera position is fairly easily identified on aerial imagery from Google Earth at a position x=491m down runway 23 and y=-161m to the left of the runway centreline.

## Camera Heading and Resolution

The first calculation is to find the camera heading (degrees) and the resolution (pixels per degree). To do this various static objects that are identifiable on aerial imagery are used:

* A Mi-2 helicopter near the centre of the frame. The length and height of this can also be used to help calibrate the camera.
* Towards the right of the frame is a pale smudge where tarmac meets grass.
* Slightly left of centre is a bright roofed house beyond the tree-line.
* There are some structures on the extreme left of the frame.
* The red building identified as the scene of the final impact can be determined by the base of the column of smoke that starts at around frame 850.

Comparing the relative frame positions of these with the actual bearings gives a camera resolution of 21.6 ±1.9 (pixels/degree), this assumes a linear field. For a video that is 640 pixels wide this corresponds to an equivalent focal length for a 35mm camera of 68±6mm. This also means that the centreline of the camera is pointing at a bearing of 238.7±2.1 degrees.

## Matching TimeLines

Several events can be seen in video B that can be compared with video A and this correlation can be used to match the timelines of the two videos:

<center>

| Video B Event | Video B Time (s) | Video A Event | Video A Time (s) | Difference (s) |
| :-- | --: | :-- | --: | ---: |
| First appearance, bearing 253.5˚ from camera |    1.4 | First appearance in video B, x=688±19 m     |   35.5 |   34.1 |
| Tyre smoke and dust                      |    1.6 | Start of drift to the right.             |   36.0 |   34.4 |
| Start of large dust plume                |   11.6 | Runway disappears                        |   46.1 |   34.5 |
| Start of smoke plume                     |   ~23 | Final impact?                            |   ~57 |   34 |

Table 1: Matching timelines of video A and B.

</center>

This gives a mean time difference of video A and B of 34.25±0.3 (s). The consistent match over 21 seconds show that the two videos are on the same timeline.

# Computed Results

## Video A

### Aircraft Position and Speed

Analysis of video A gives:

* The aircraft position from overflying landmarks, differentiating this give the aircraft's ground speed.
* The aircraft's passage over the runway slabs gives the aircrafts ground speed, integrating this gives the distance that the aircraft has covered.

Here is a plot of distance from the start of runway 23 over time from video A, the mid points are fitted to a third order polynomial. The right hand graph shows the comparison where the two measurements overlap:

<center>
<img src="plots/tile_distance.svg" width="300" />&nbsp;
<img src="plots/tile_distance_cmp.svg" width="300" />&nbsp;
</center>

The difference between the two techniques is 5m or less.

### Aircraft Ground Speed

The aircraft's ground speed can be calculated from video A by:

* The differential of the aircraft's position when overflying landmarks.
* Directly from the aircraft's rate of passage over the runway slabs.

Here is the ground speed by the two techniques. The right hand graph shows the comparison where the two measurements overlap:

<center>
<img src="plots/speed.svg" width="300" />&nbsp;
<img src="plots/speed_cmp.svg" width="300" />&nbsp;
</center>

The difference is 1.4 to 2.2 m/s over this interval with the fitted data which is just about within the error terms of each if centred on the respective fitted data.

## Video B

Various unsuccessful attempts were made to identify the aircraft position and speed from video B (the security camera video). The following measurements, once the camera heading and resolution were known, could be converted to the aircraft's position:

1. The bearing of the aircraft from the camera.
2. The range of the aircraft from the apparent height of the top of the tail above ground.
3. The range of the aircraft from the apparent span of the wings.

A problem for the latter two is that the measurements are often only a few pixels wide with a correspondingly large uncertainty. Beyond t=40.2 the data from the latter two techniques is deemed unreliable due to the low resolution of the camera and the indistinct image of the aircraft.

The calculated distance down the runway by these three methods agree rather roughly in magnitude as shown below on the left (the distance data from the slab measurements is also shown for comparison). However when differentiated to obtain ground speed the results are implausible except for the bearing data, as seen on the right.

<center>
<img src="plots/video_b_distance.svg" width="300" />&nbsp;
<img src="plots/video_b_speed.svg" width="300" />&nbsp;
</center>

The poor results from this analysis could be for many reasons; the low resolution of the video, measurement error, non-linear camera field and so on. Even the bearing data does not make sense giving a de-acceleration of around -5m/s, if this were true the aircraft would have stopped well before the boundary fence which was not the case. The following graph compares the ground speed from the slab speed data of video A to the bearing data of video B:

<center>
<img src="plots/speed_cmp_slab_video_b.svg" width="300" />&nbsp;
</center>

### Conclusion for the Data From Video B

The data obtained from video B is not useful for calculating the position or speed of the aircraft. The data from video B is useful in that it can tie visible events to the motion of the aircraft seen in video A, for example the smoke and dust appearing from the tyres and the start of the aircraft swinging to the right.

The video A data is used henceforth to compute the trajectory of the aircraft.

## Acceleration

The ground speed if the aircraft computed from video A can be differentiated to give the longitudinal acceleration:

<center>
<img src="plots/acceleration.svg" width="300" />&nbsp;
</center>

There are no visible discontinuities of sudden changes of acceleration such as might be caused by a tyre burst or running of the runway. Possibly this is because of the smoothing caused by the curve fitting process.

# Motion After t=45.7 Seconds

The last computed position at t=45.7 seconds is:

<center>

| Time | Position | Ground Speed | Acceleration |
| :--: | :--: | :--: | :--: |
| 45.7 s | 1442 ±48 m | 60.0 ±3.7 m/s, 117 ±12 knots | -3.7 ±0.3 m/s^2 |

Table 2: Last computed position.

</center>

There are no landmarks or visible features in video A after t=45.7 seconds that can be used to give speed or position but there is a collision with the boundary fence that can be used to estimate these values.

### The Boundary Fence Impact

At t=56.1s the aircraft collides with the boundary fence and this fence is readily identifiable on the aerial imagery as being 1853m from the start of runway 23, 200m beyond the runway end. The sequence below shows four consecutive frames from the video of the starboard undercarriage collapse as the aircraft goes through the airfield boundary. 

<center>
<img src="img/frame1684.png" width="120" alt="frame 1684"/>&nbsp;<img src="img/frame1685.png" width="120" />&nbsp;<img src="img/frame1686.png" width="120" />&nbsp;<img src="img/frame1687.png" width="120" />
</center>

The first frame [1684] shows the moment before impact, the obstruction is on the left which looks like as substantial concrete block, the dark disc at the bottom is the tyre and the silver vertical is the undercarriage leg. The second frame (t=56.1s) shows the moment of impact and the last two frames show progressive collapse of the starboard landing leg. The last frame is rotated somewhat to right, most likely due to the forces on the person filming which would naturally rotate a hand held camera to the left.

Here are those frames as a composite image adjusting, approximately, for alignment and tilt:

<center>
<img src="img/frame1684-1687_composite.png" width=600"  alt="Composite of frames 1684-1687" />
</center>

### Boundary Fence Impact Speed and Acceleration

The impact point is 1853m from the start of runway 23 and 10.4 seconds after the last known position. Given the initial speed and initial position the mean speed can be calculated. Assuming constant acceleration the impact speed and the acceleration can be calculated. For example, given v initial as 60.0 m/s at 1442 m:

* Then v mean is distance over time; (1853 - 1442) / 10.4 = 39.5 m/s.
* So v final is 39.5 - (60.0 - 39.5) = 19.1 m/s
* Giving an average acceleration of (19.0 - 60.0) / 10.4 = -3.9 m/s^2 . 

Here is that calculation for the mid point and the +/- error estimates.

<center>

| Calculation | v initial in m/s (knots) | d initial (m) | a (m/s^2) | v impact in m/s (knots) |
| :--: | :--: | :--: | :--: | :--: |
| Mid point | 60.0 (117) | 1442 | -3.9 | 19.1 (37) |
| +ve error | 63.8 (124) | 1489 | -5.5 | 6.2 (12) |
| -ve error | 56.3 (109) | 1394 | -2.3 | 32.0 (62) |

Table 3: Estimated boundary fence impact speed.

</center>

The mid point data computed acceleration of -3.9 m/s^2 agrees very well with the last computed acceleration of -3.7 ±0.3 m/s^2 . That the mid estimate is correct is further supported by the ballistic (i.e. uncontrolled) trajectory of the aircraft to the final impact.

## Final Impact

36m beyond the boundary fence is a building that is where the aircraft finally stopped. Assuming the (de)acceleration is the same as before the boundary fence impact and ignoring any speed reduction caused by the boundary fence impact the final impact speed would be:

<center>

| Calculation | v boundary fence, from table 3  in m/s (knots) | a, from table 3 (m/s^2) | Calculated distance to full stop (m) | v impact at 36m (m/s, knots) |
| :--: | :--: | :--: | :--: | :--: |
| Mid point | 19.1 (37) | -3.9 | 46.4 | 9.1 (18) |
| +ve error | 6.2 (12) | -5.5 | 3.5 | No impact |
| -ve error | 32.0 (62) | -2.3 | 219| 29.3 (57) |

Table 4: Estimated final impact speed.

</center>

Images of the aftermath suggest that the mid-point calculation is probably correct and that the final impact occurred at roughly 9 m/s (18 knots). This can be regarded as an upper bound as it ignores the speed lost by the collision with the boundary fence and the likely increase of deceleration after the undercarriage collapsed.

# Summary of Events

Combining all the data gives the following summary of events, time is in video A time, position is from the start of runway 23:

<center>

| Time (s) | Position (m) | Ground Speed (m/s, knots) | Acceleration (m/s^2 ) | Description |
| ---: | ---: | ---: | ---: | :--- |
|  0.0 |    -2481±98 |     82.8±2.0,   161±4 |      1.2±0.2 |  Video start. |
| 17.0 |     -964±44 |     92.7±3.5,   180±7 |     0.0±0.1 |  Maximum ground speed. |
| 27.5 |        0±14 |     88.6±1.9,   172±4 |     -0.7±0.1 |  Threshold. |
| 33.8 |      549±17 |     84.3±0.8,   164±2 |     -1.0±0.1 |  Touchdown. |
| 35.5 |      688±19 |     82.4±1.0,   160±2 |     -1.2±0.2 |  First appearance in video B. |
| 36.0 |      731±19 |     81.8±1.1,   159±2 |     -1.2±0.3 |  Start of drift to the right. Tyre smoke and dust observed in video B. |
| 45.7 |     1442±48 |     60.0±3.7,   117±7 |     -3.7±0.3 |  Last speed measurement. |
| 46.1 |     1463±49 |     ~58.7±3.6,   114±7 |     -3.9±0.4 |  Runway disappears. Dust plume observed in video B. Speed and distance are extrapolated. |
| 56.1 |     1853±10 |     Around: 19, 37 |     Around -3.9 |  Impact with boundary fence. |
| ~57 |     1889±10 |    Less than: 9, 18 |  |  Final impact. Smoke column starts in video B. |

Table 5: Selected Events

</center>

# Sources of information Subsequently Discovered

These sources of information were discovered after this initial investigation ended on 2019-08-26:

* The Russian Accident Investigation:
[https://mak-iac.org/en/rassledovaniya/an-24rv-ra-47366-27-06-2019/](https://mak-iac.org/en/rassledovaniya/an-24rv-ra-47366-27-06-2019/)
* Preliminary Accident Report (in Russian) Created 1 Aug 2019 at 10:16, modified 11 Oct 2019 at 13:30:
[https://mak-iac.org/upload/iblock/870/report_ra-47366_pr.pdf](https://mak-iac.org/upload/iblock/870/report_ra-47366_pr.pdf)




