#include <string.h>
#include <stdlib.h>	
#include <stdio.h>

#include <linux/types.h>
#include <fcntl.h>
#include "2inch13_epd.h"
#include "sg_lgpio.h"
#include <unistd.h>
#include <stdint.h>
#include <linux/types.h> 

//define pin conection in BCM number
/****************************
* PIN_CS      8 
* PIN_RST     17 
* PIN_DC      25
* PIN_BBUSY   24
***************************/

void EPD_GPIO_Init(void)
{
    Lgpio_export(); 
    Lgpio_set_pinmode(PIN_RST,LGPIO_OUTPUT);
    Lgpio_set_pinmode(PIN_DC,LGPIO_OUTPUT);
    Lgpio_set_pinmode(PIN_BUSY,LGPIO_INPUT); 
    LG_SPI_Init(0, 0, 8000000);
}

void EPD_Display(unsigned char *Image)
{
    unsigned int width, Height,i,j;
    width = (EPD_WIDTH % 8 == 0)? (EPD_WIDTH / 8 ): (EPD_WIDTH / 8 + 1);
    Height = EPD_HEIGHT;

    Epaper_Write_Command(0x24);
    for ( j = 0; j < Height; j++) 
	{
        for ( i = 0; i < width; i++) 
		{
           Epaper_Write_Data(Image[i + j * width]);
        }
    }
    EPD_Update();		 
}


void Epaper_READBUSY(void)
{ 
	while(1)
	{	 //=1 BUSY
		 if(Lgpio_read_pin(PIN_BUSY)==LGPIO_LOW) break;
	}  
}

void Epaper_Write_Command(unsigned char cmd)
{
	Lgpio_write_pin(PIN_DC,LGPIO_LOW);  // D/C#   0:command  1:data
	LG_SPI_writebyte(cmd);
}

void Epaper_Write_Data(unsigned char data)
{
	Lgpio_write_pin(PIN_DC,LGPIO_HIGH); // D/C#   0:command  1:data
	LG_SPI_writebyte(data);
}

/////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////

//SSD1681
void EPD_HW_Init(void)
{
	Lgpio_write_pin(PIN_RST,LGPIO_LOW);  // Module reset   
	delay(10);//At least 10ms delay 
	Lgpio_write_pin(PIN_RST,LGPIO_HIGH); 
	delay(10); //At least 10ms delay 
		
	Epaper_READBUSY();   
	Epaper_Write_Command(0x12);  //SWRESET
	Epaper_READBUSY();   
			
	Epaper_Write_Command(0x01); //Driver output control     
	delay(10); //At least 10ms delay 	
	Epaper_Write_Data(0xF9);
	delay(10); //At least 10ms delay 
	Epaper_Write_Data(0x00);
	delay(10); //At least 10ms delay 
	Epaper_Write_Data(0x00);

	Epaper_Write_Command(0x11); //data entry mode       
	Epaper_Write_Data(0x02);

	Epaper_Write_Command(0x44); //set Ram-X address start/end position   
	Epaper_Write_Data(0x0F);
	Epaper_Write_Data(0x00);    //0x0F-->(15+1)*8=128

	Epaper_Write_Command(0x45); //set Ram-Y address start/end position          
	Epaper_Write_Data(0x00);    //0x127-->(295+1)=296
	Epaper_Write_Data(0x00);
	Epaper_Write_Data(0xF9);
	Epaper_Write_Data(0x00); 

	Epaper_Write_Command(0x4E);   // set RAM x address count to 0;
	Epaper_Write_Data(0x0F);
	Epaper_Write_Command(0x4F);   // set RAM y address count to 296;    
	Epaper_Write_Data(0x00);
	Epaper_Write_Data(0x00);
	
	Epaper_Write_Command(0x3C); //BorderWavefrom
	Epaper_Write_Data(0x05);	
	
	Epaper_Write_Command(0x21); //BorderWavefrom
	Epaper_Write_Data(0x00);	
	Epaper_Write_Data(0x80);
				
	Epaper_Write_Command(0x18); //Read built-in temperature sensor
	Epaper_Write_Data(0x80);	

	Epaper_READBUSY();
	
}
void EPD_HW_Init_Fast(void)
{
	Lgpio_write_pin(PIN_RST,LGPIO_LOW); // Module reset     
	delay(10);//At least 10ms delay 
	Lgpio_write_pin(PIN_RST,LGPIO_HIGH); 
	delay(10); //At least 10ms delay 
		
	Epaper_Write_Command(0x12);  //SWRESET
	Epaper_READBUSY();   
	Epaper_Write_Command(0x01); 
	Epaper_Write_Data(0x27);
    Epaper_Write_Data(0x01);
    Epaper_Write_Data(0x00);	
	
	Epaper_Write_Command(0x11); //Read built-in temperature sensor
	Epaper_Write_Data(0x02);	

	Epaper_Write_Command(0x44); 
	Epaper_Write_Data(0x0F);
    Epaper_Write_Data(0x00);
    
	Epaper_Write_Command(0x45); 
	Epaper_Write_Data(0x00);
    Epaper_Write_Data(0x00);
    Epaper_Write_Data(0xF9);
    Epaper_Write_Data(0x00);
			
	Epaper_Write_Command(0x18); //Read built-in temperature sensor
	Epaper_Write_Data(0x80);	
				
	Epaper_Write_Command(0x22); // Load temperature value
	Epaper_Write_Data(0xB1);		
	Epaper_Write_Command(0x20);	
	Epaper_READBUSY(); 
	
	Epaper_Write_Command(0x4E); 
	Epaper_Write_Data(0x0F);  
	Epaper_Write_Command(0x4F); 
	Epaper_Write_Data(0x00); 
	Epaper_Write_Data(0x00);   
	
	Epaper_Write_Command(0x1A); // Write to temperature register
	Epaper_Write_Data(0x64);		
	Epaper_Write_Data(0x00);	
							
	Epaper_Write_Command(0x22); // Load temperature value
	Epaper_Write_Data(0x91);		
	Epaper_Write_Command(0x20);	
	Epaper_READBUSY();   
}

void EPD_HW_Init_GUI(void)
{
	Lgpio_write_pin(PIN_RST,LGPIO_LOW); // Module reset    
	delay(10);//At least 10ms delay 
	Lgpio_write_pin(PIN_RST,LGPIO_HIGH); 
	delay(10); //At least 10ms delay 
	
	Epaper_READBUSY();   
	Epaper_Write_Command(0x12);  //SWRESET
	Epaper_READBUSY();   
		
	Epaper_Write_Command(0x01); //Driver output control 
	delay(10); //At least 10ms delay 	
	Epaper_Write_Data(0xF9);
	delay(10); //At least 10ms delay 
	Epaper_Write_Data(0x00);
	delay(10); //At least 10ms delay 
	Epaper_Write_Data(0x00);//0x00:Show normal 0x01:Show mirror

	Epaper_Write_Command(0x11); //data entry mode       
	Epaper_Write_Data(0x03);

	Epaper_Write_Command(0x44); //set Ram-X address start/end position   
	Epaper_Write_Data(0x00);
	Epaper_Write_Data(0x0F);    //0x0F-->(15+1)*8=128

	Epaper_Write_Command(0x45); //set Ram-Y address start/end position          
	Epaper_Write_Data(0x00);    //0x127-->(199+1)=296
	Epaper_Write_Data(0x00);
	Epaper_Write_Data(0xF9);
	Epaper_Write_Data(0x00); 

	Epaper_Write_Command(0x3C); //BorderWavefrom
	Epaper_Write_Data(0x05);	
	  	
    Epaper_Write_Command(0x18); //Read built-in temperature sensor
	Epaper_Write_Data(0x80);	

	Epaper_Write_Command(0x4E);   // set RAM x address count to 0;
	Epaper_Write_Data(0x00);
	Epaper_Write_Command(0x4F);   // set RAM y address count to 0   
	Epaper_Write_Data(0x00);
	Epaper_Write_Data(0x00);
    Epaper_READBUSY();
	
}
/////////////////////////////////////////////////////////////////////////////////////////
/*When the electronic paper screen is updated, do not unplug the electronic paper to avoid damage to the screen*/

void EPD_Update(void)
{   
  Epaper_Write_Command(0x22); //Display Update Control
  Epaper_Write_Data(0xF7);   
  Epaper_Write_Command(0x20); //Activate Display Update Sequence
  Epaper_READBUSY();   

}
void EPD_Update_Fast(void)
{   
  Epaper_Write_Command(0x22); //Display Update Control
  Epaper_Write_Data(0xC7);   
  Epaper_Write_Command(0x20); //Activate Display Update Sequence
  Epaper_READBUSY();   

}
/*When the electronic paper screen is updated, do not unplug the electronic paper to avoid damage to the screen*/
void EPD_Part_Update(void)
{
	Epaper_Write_Command(0x22); //Display Update Control
	Epaper_Write_Data(0xFF);   
	Epaper_Write_Command(0x20); //Activate Display Update Sequence
	Epaper_READBUSY(); 			
}
//////////////////////////////All screen update////////////////////////////////////////////
//because the screen width is 122(x-axis direction),the high 6 bits of the
//first byte of each column are meaningless
void EPD_WhiteScreen_ALL(const unsigned char *datas)
{
	unsigned int i,j,x_bytes; 	
    Epaper_Write_Command(0x24);   //write RAM for black(0)/white (1)
   //for(i=0;i<4000;i++)
   //{               
       //Epaper_Write_Data(*datas);
	   //datas++;
   //} 
    x_bytes = EPD_WIDTH/8+1;
    for(j=0;j<EPD_HEIGHT;j++)//
    {
		for(i=0;i<x_bytes;i++)
		{    
			if(i==0)  
			{
			    Epaper_Write_Data((datas[i+j*x_bytes]>>6)|0xfc);
			}
			else
			{
				Epaper_Write_Data((datas[i+j*x_bytes-1]<<2)|(datas[i+j*x_bytes]>>6));
			}         
			//datas++;
		}
	}
   EPD_Update();	 
}

//because the screen width is 122(x-axis direction),the high 6 bits of the
//first byte of each column are meaningless
void EPD_WhiteScreen_ALL_Fast(const unsigned char *datas)
{
	unsigned int i,j,x_bytes; 	
    Epaper_Write_Command(0x24);   //write RAM for black(0)/white (1)
   //for(i=0;i<4000;i++)
   //{               
       //Epaper_Write_Data(*datas);
	   //datas++;
   //} 
    x_bytes = EPD_WIDTH/8+1;
    for(j=0;j<EPD_HEIGHT;j++)//
    {
		for(i=0;i<x_bytes;i++)
		{    
			if(i==0)  
			{
			    Epaper_Write_Data((datas[i+j*x_bytes]>>6)|0xfc);
			}
			else
			{
				Epaper_Write_Data((datas[i+j*x_bytes-1]<<2)|(datas[i+j*x_bytes]>>6));
			}         
			//datas++;
		}
	}
	 
   EPD_Update_Fast();	 
}
///////////////////////////Part update//////////////////////////////////////////////
//The x axis is reduced by one byte, and the y axis is reduced by one pixel.
//because the screen width is 122(x-axis direction),the high 6 bits of the
//first byte of each column are meaningless
void EPD_SetRAMValue_BaseMap( const unsigned char * datas)
{
	unsigned int i,j,x_bytes;   
	
    Epaper_Write_Command(0x24);   //Write Black and White image to RAM
    x_bytes = EPD_WIDTH/8+1;
    for(j=0;j<EPD_HEIGHT;j++)//
    {
		for(i=0;i<x_bytes;i++)
		{    
			if(i==0)  
			{
			    Epaper_Write_Data((datas[i+j*x_bytes]>>6)|0xfc);
			}
			else
			{
				Epaper_Write_Data((datas[i+j*x_bytes-1]<<2)|(datas[i+j*x_bytes]>>6));
			}         
			//datas++;
		}
	}
	//datas=datas_flag;
    Epaper_Write_Command(0x26);   //Write Black and White image to RAM
    for(j=0;j<EPD_HEIGHT;j++)
    {
		for(i=0;i<x_bytes;i++)
		{    
			if(i==0)  
			{
			    Epaper_Write_Data((datas[i+j*x_bytes]>>6)|0xfc);
			}
			else
			{
				Epaper_Write_Data((datas[i+j*x_bytes-1]<<2)|(datas[i+j*x_bytes]>>6));
			}         
			//datas++;
		}
	}
    EPD_Update();		 
	 
}
void EPD_Dis_Part(unsigned int x_start,unsigned int y_start,const unsigned char * datas,unsigned int PART_COLUMN,unsigned int PART_LINE)
{
	unsigned int i;  
	unsigned int x_end,y_start1,y_start2,y_end1,y_end2;
	x_start=x_start/8;
	x_end=0X0F-(x_start+PART_LINE/8-1); 
	x_start=0X0F-x_start;
	
	y_start1=0;
	y_start2=y_start;
	if(y_start>=256)
	{
		y_start1=y_start2/256;
		y_start2=y_start2%256;
	}
	y_end1=0;
	y_end2=y_start+PART_COLUMN-1;
	if(y_end2>=256)
	{
		y_end1=y_end2/256;
		y_end2=y_end2%256;		
	}		

		// Add hardware reset to prevent background color change
	Lgpio_write_pin(PIN_RST,LGPIO_LOW); // Module reset   
	delay(10);//At least 10ms delay 
	Lgpio_write_pin(PIN_RST,LGPIO_HIGH); 
	delay(10); //At least 10ms delay 	
	  //Lock the border to prevent flashing
	Epaper_Write_Command(0x3C); //BorderWavefrom,
	Epaper_Write_Data(0x80);
	
	Epaper_Write_Command(0x44);       // set RAM x address start/end, in page 35
	Epaper_Write_Data(x_start);    // RAM x address start at 00h;
	Epaper_Write_Data(x_end);    // RAM x address end at 0fh(15+1)*8->128 
	Epaper_Write_Command(0x45);       // set RAM y address start/end, in page 35
	Epaper_Write_Data(0XF9-y_start2);    // RAM y address start at 0127h;
	Epaper_Write_Data(0XF9-y_start1);    // RAM y address start at 0127h;
	Epaper_Write_Data(0XF9-y_end2);    // RAM y address end at 00h;
	Epaper_Write_Data(0XF9-y_end1);    // ????=0	


	Epaper_Write_Command(0x4E);   // set RAM x address count to 0;
	Epaper_Write_Data(x_start); 
	Epaper_Write_Command(0x4F);   // set RAM y address count to 0X127;    
	Epaper_Write_Data(y_start2);
	Epaper_Write_Data(y_start1);
	
	
	Epaper_Write_Command(0x24);   //Write Black and White image to RAM
    for(i=0;i<PART_COLUMN*PART_LINE/8;i++)
    {                         
        Epaper_Write_Data(*datas);
		datas++;
    } 
	EPD_Part_Update();

}

void EPD_DeepSleep(void)
{  	
    Epaper_Write_Command(0x10); //enter deep sleep
    Epaper_Write_Data(0x01); 
    delay(100);
}


/////////////////////////////////Single display////////////////////////////////////////////////

void EPD_WhiteScreen_White(void)

{
    unsigned int i,k;
	Epaper_Write_Command(0x24);   //write RAM for black(0)/white (1)
	for(k=0;k<250;k++)
    {
	    for(i=0;i<16;i++)
		{
		    Epaper_Write_Data(0xff);
		}
    }
	EPD_Update();
}

/////////////////////////////////////TIME///////////////////////////////////////////////////
void EPD_Dis_Part_myself(unsigned int x_startA,unsigned int y_startA,const unsigned char * datasA,
	                       unsigned int x_startB,unsigned int y_startB,const unsigned char * datasB,
												 unsigned int x_startC,unsigned int y_startC,const unsigned char * datasC,
												 unsigned int x_startD,unsigned int y_startD,const unsigned char * datasD,
											   unsigned int x_startE,unsigned int y_startE,const unsigned char * datasE,
												 unsigned int PART_COLUMN,unsigned int PART_LINE
	                      )
{
		unsigned int i;  
		unsigned int x_end,y_start1,y_start2,y_end1,y_end2;
		
		//Data A////////////////////////////
		x_startA=x_startA/8;//Convert to byte
		x_end=0x0f-(x_startA+PART_LINE/8-1); 
		x_startA = 0X0F-x_startA;
		
		y_start1=0;
		y_start2=y_startA-1;
		if(y_startA>=256)
		{
				y_start1=y_start2/256;
				y_start2=y_start2%256;
		}
		y_end1=0;
		y_end2=y_startA+PART_COLUMN-1;
		if(y_end2>=256)
		{
				y_end1=y_end2/256;
				y_end2=y_end2%256;		
		}		
		
		// Add hardware reset to prevent background color change
		Lgpio_write_pin(PIN_RST,LGPIO_LOW); 
		//digitalWrite(PIN_RST, 0);  // Module reset   
		delay(10);//At least 10ms delay 
		Lgpio_write_pin(PIN_RST,LGPIO_HIGH); 
		//digitalWrite(PIN_RST, 1);
		delay(10); //At least 10ms delay 	
			//Lock the border to prevent flashing
		Epaper_Write_Command(0x3C); //BorderWavefrom,
		Epaper_Write_Data(0x80);	
		
		Epaper_Write_Command(0x44);       // set RAM x address start/end, in page 35
		Epaper_Write_Data(x_startA);    // RAM x address start at 00h;
		Epaper_Write_Data(x_end);    // RAM x address end at 0fh(15+1)*8->128 
		Epaper_Write_Command(0x45);       // set RAM y address start/end, in page 35
		Epaper_Write_Data(0XF9-y_start2);    // RAM y address start at 0127h;
		Epaper_Write_Data(0XF9-y_start1);    // RAM y address start at 0127h;
		Epaper_Write_Data(0XF9-y_end2);    // RAM y address end at 00h;
		Epaper_Write_Data(0XF9-y_end1);    


		Epaper_Write_Command(0x4E);   // set RAM x address count to 0;
		Epaper_Write_Data(x_startA); 
		Epaper_Write_Command(0x4F);   // set RAM y address count to 0X127;    
		Epaper_Write_Data(y_start2);
		Epaper_Write_Data(y_start1);
	
	
	 Epaper_Write_Command(0x24);   //Write Black and White image to RAM
    for(i=0;i<PART_COLUMN*PART_LINE/8;i++)
    {                         
		Epaper_Write_Data(*datasA);
		datasA++;
    } 
	//Data B/////////////////////////////////////
	x_startB=x_startB/8;//Convert to byte
	x_end=0X0F-(x_startB+PART_LINE/8-1); 
	x_startB=0X0F-x_startB;
	
	y_start1=0;
	y_start2=y_startB-1;
	if(y_startB>=256)
	{
		y_start1=y_start2/256;
		y_start2=y_start2%256;
	}
	y_end1=0;
	y_end2=y_startB+PART_COLUMN-1;
	if(y_end2>=256)
	{
		y_end1=y_end2/256;
		y_end2=y_end2%256;		
	}		
	
	Epaper_Write_Command(0x44);       // set RAM x address start/end, in page 35
	Epaper_Write_Data(x_startB);    // RAM x address start at 00h;
	Epaper_Write_Data(x_end);    // RAM x address end at 0fh(15+1)*8->128 
	Epaper_Write_Command(0x45);       // set RAM y address start/end, in page 35
	Epaper_Write_Data(0XF9-y_start2);    // RAM y address start at 0127h;
	Epaper_Write_Data(0XF9-y_start1);    // RAM y address start at 0127h;
	Epaper_Write_Data(0XF9-y_end2);    // RAM y address end at 00h;
	Epaper_Write_Data(0XF9-y_end1);   


	Epaper_Write_Command(0x4E);   // set RAM x address count to 0;
	Epaper_Write_Data(x_startB); 
	Epaper_Write_Command(0x4F);   // set RAM y address count to 0X127;    
	Epaper_Write_Data(y_start2);
	Epaper_Write_Data(y_start1);
	
	
	Epaper_Write_Command(0x24);   //Write Black and White image to RAM
    for(i=0;i<PART_COLUMN*PART_LINE/8;i++)
    {                         
        Epaper_Write_Data(*datasB);
		datasB++;
    } 	 
	 
	//Data C//////////////////////////////////////
	x_startC=x_startC/8;//Convert to byte
	x_end=0X0F-(x_startC+PART_LINE/8-1); 
	x_startC=0X0F-x_startC;
	
	y_start1=0;
	y_start2=y_startC-1;
	if(y_startC>=256)
	{
			y_start1=y_start2/256;
			y_start2=y_start2%256;
	}
	y_end1=0;
	y_end2=y_startC+PART_COLUMN-1;
	if(y_end2>=256)
	{
			y_end1=y_end2/256;
			y_end2=y_end2%256;		
	}		
	
	Epaper_Write_Command(0x44);       // set RAM x address start/end, in page 35
	Epaper_Write_Data(x_startC);    // RAM x address start at 00h;
	Epaper_Write_Data(x_end);    // RAM x address end at 0fh(15+1)*8->128 
	Epaper_Write_Command(0x45);       // set RAM y address start/end, in page 35
	Epaper_Write_Data(0XF9-y_start2);    // RAM y address start at 0127h;
	Epaper_Write_Data(0XF9-y_start1);    // RAM y address start at 0127h;
	Epaper_Write_Data(0XF9-y_end2);    // RAM y address end at 00h;
	Epaper_Write_Data(0XF9-y_end1);   


	Epaper_Write_Command(0x4E);   // set RAM x address count to 0;
	Epaper_Write_Data(x_startC); 
	Epaper_Write_Command(0x4F);   // set RAM y address count to 0X127;    
	Epaper_Write_Data(y_start2);
	Epaper_Write_Data(y_start1);
	
	
	Epaper_Write_Command(0x24);   //Write Black and White image to RAM
    for(i=0;i<PART_COLUMN*PART_LINE/8;i++)
    {                         
        Epaper_Write_Data(*datasC);
		datasC++;
    } 	 	 
 	 
	//Data D//////////////////////////////////////
	x_startD=x_startD/8;//Convert to byte
	x_end=0X0F-(x_startD+PART_LINE/8-1); 
	x_startD=0X0F-x_startD;
	
	y_start1=0;
	y_start2=y_startD-1;
	if(y_startD>=256)
	{
		y_start1=y_start2/256;
		y_start2=y_start2%256;
	}
	y_end1=0;
	y_end2=y_startD+PART_COLUMN-1;
	if(y_end2>=256)
	{
		y_end1=y_end2/256;
		y_end2=y_end2%256;		
	}		
	
	Epaper_Write_Command(0x44);       // set RAM x address start/end, in page 35
	Epaper_Write_Data(x_startD);    // RAM x address start at 00h;
	Epaper_Write_Data(x_end);        // RAM x address end at 0fh(15+1)*8->128 
	Epaper_Write_Command(0x45);       // set RAM y address start/end, in page 35
	Epaper_Write_Data(0XF9-y_start2);    // RAM y address start at 0127h;
	Epaper_Write_Data(0XF9-y_start1);    // RAM y address start at 0127h;
	Epaper_Write_Data(0XF9-y_end2);    // RAM y address end at 00h;
	Epaper_Write_Data(0XF9-y_end1);    


	Epaper_Write_Command(0x4E);   // set RAM x address count to 0;
	Epaper_Write_Data(x_startD); 
	Epaper_Write_Command(0x4F);   // set RAM y address count to 0X127;    
	Epaper_Write_Data(y_start2);
	Epaper_Write_Data(y_start1);
	
	
	Epaper_Write_Command(0x24);   //Write Black and White image to RAM
    for(i=0;i<PART_COLUMN*PART_LINE/8;i++)
    {                         
        Epaper_Write_Data(*datasD);
		datasD++;
    } 
	//Data E//////////////////////////////////////
	x_startE=x_startE/8;//Convert to byte
	x_end=0X0F-(x_startE+PART_LINE/8-1); 
	x_startE=0X0F-x_startE;
	y_start1=0;
	y_start2=y_startE-1;
	if(y_startE>=256)
	{
		y_start1=y_start2/256;
		y_start2=y_start2%256;
	}
	y_end1=0;
	y_end2=y_startE+PART_COLUMN-1;
	if(y_end2>=256)
	{
		y_end1=y_end2/256;
		y_end2=y_end2%256;		
	}		
	
	Epaper_Write_Command(0x44);       // set RAM x address start/end, in page 35
	Epaper_Write_Data(x_startE);    // RAM x address start at 00h;
	Epaper_Write_Data(x_end);    // RAM x address end at 0fh(15+1)*8->128 
	Epaper_Write_Command(0x45);       // set RAM y address start/end, in page 35
	Epaper_Write_Data(0XF9-y_start2);    // RAM y address start at 0127h;
	Epaper_Write_Data(0XF9-y_start1);    // RAM y address start at 0127h;
	Epaper_Write_Data(0XF9-y_end2);    // RAM y address end at 00h;
	Epaper_Write_Data(0XF9-y_end1);    


	Epaper_Write_Command(0x4E);   // set RAM x address count to 0;
	Epaper_Write_Data(x_startE); 
	Epaper_Write_Command(0x4F);   // set RAM y address count to 0X127;    
	Epaper_Write_Data(y_start2);
	Epaper_Write_Data(y_start1);
	
	
	Epaper_Write_Command(0x24);   //Write Black and White image to RAM
    for(i=0;i<PART_COLUMN*PART_LINE/8;i++)
    {                         
        Epaper_Write_Data(*datasE);
		datasE++;
    } 	  
	EPD_Part_Update();

}

/***********************************************************
						end file
***********************************************************/

