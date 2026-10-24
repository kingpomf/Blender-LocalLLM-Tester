"""Pure-Python pin lathe: explicit (radius, height), closed caps, two neck bands."""
from math import cos, sin, pi

PROFILE=[(.036,0.0),(.041,.004),(.052,.025),(.0605,.060),(.0605,.100),
         (.052,.150),(.040,.200),(.028,.240),(.022,.260),(.022,.270),
         (.022,.276),(.022,.282),(.022,.288),(.022,.294),(.022,.300),
         (.025,.312),(.032,.325),(.036,.340),(.035,.355),(.029,.370),
         (.018,.378),(.008,.380)]
BANDS=[(.270,.276),(.288,.294)]


def build_pin(segments=24):
    assert type(segments) is int and 12<=segments<=48
    vertices=[]; faces=[]; indices=[]
    for radius,height in PROFILE:
        assert radius>0
        vertices.extend((radius*cos(2*pi*i/segments),radius*sin(2*pi*i/segments),height) for i in range(segments))
    for level in range(len(PROFILE)-1):
        middle=(PROFILE[level][1]+PROFILE[level+1][1])/2
        band=any(low<middle<high for low,high in BANDS)
        for index in range(segments):
            following=(index+1)%segments
            faces.append((level*segments+index,level*segments+following,(level+1)*segments+following,(level+1)*segments+index))
            indices.append(1 if band else 0)
    top=len(vertices); vertices.append((0,0,.381))
    bottom=len(vertices); vertices.append((0,0,0))
    for index in range(segments):
        following=(index+1)%segments
        faces.extend([(top,(len(PROFILE)-1)*segments+index,(len(PROFILE)-1)*segments+following),
                      (bottom,following,index)])
        indices.extend([0,0])
    return vertices,faces,indices
