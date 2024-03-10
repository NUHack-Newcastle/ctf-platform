/*
	Flag Generating Code for Reverse Engineering Exercises

	Closed Source Header: CODE NOT TO BE DISTRIBUTED TO PARTICIPANTS

	24 November 2022
	Copyright CyberSoc (c) 2022
*/

#ifndef FLAG
	#error "FLAG is not defined."
#endif /* VER_MAJOR */

char __generated_flag[sizeof(FLAG)];

_Static_assert(sizeof(FLAG)-1 == 22, "FLAG must be exactly 22 characters");

volatile char encrypted_bytes[sizeof(FLAG)-1] = {
	FLAG[0] ^ _KEY_BYTE01,
	FLAG[1] ^ _KEY_BYTE02,
	FLAG[2] ^ _KEY_BYTE03,
	FLAG[3] ^ _KEY_BYTE04,
	FLAG[4] ^ _KEY_BYTE05,
	FLAG[5] ^ _KEY_BYTE06,
	FLAG[6] ^ _KEY_BYTE07,
	FLAG[7] ^ _KEY_BYTE08,
	FLAG[8] ^ _KEY_BYTE09,
	FLAG[9] ^ _KEY_BYTE10,
	FLAG[10] ^ _KEY_BYTE11,
	FLAG[11] ^ _KEY_BYTE12,
	FLAG[12] ^ _KEY_BYTE13,
	FLAG[13] ^ _KEY_BYTE14,
	FLAG[14] ^ _KEY_BYTE15,
	FLAG[15] ^ _KEY_BYTE16,
	FLAG[16] ^ _KEY_BYTE17,
	FLAG[17] ^ _KEY_BYTE18,
	FLAG[18] ^ _KEY_BYTE19,
	FLAG[19] ^ _KEY_BYTE20,
	FLAG[20] ^ _KEY_BYTE21,
	FLAG[21] ^ _KEY_BYTE22
};

unsigned long lfsr = _LFSR_SEED;

for(int fi=0;fi<sizeof(FLAG)-1;fi++){
	for(int li=0;li<32;li++){
		unsigned char lfsr_newbit = ((lfsr & 1) ^ ((lfsr >> 1) & 1) ^ ((lfsr >> 3) & 1) ^ ((lfsr >> 5) & 1) ^ ((lfsr >> 8) & 1) ^ ((lfsr >> 13) & 1) ^ ((lfsr >> 21) & 1));
		lfsr >>= 1;
		lfsr |= (lfsr_newbit << 31) & 0xffffffff;
	}

	// useless nonsense to make the assembly hard to reverse
	// they should not be reversing the flag generation so lets discourage it
	unsigned long important_data = lfsr ^ 0xe85dee35;
	for (unsigned int oi=0;oi<(((lfsr - 3) * important_data>>7)&1);oi++){
		if(lfsr > important_data + 98047552)
			important_data *= lfsr << 9 >> 2 * (lfsr +3);
		else if(lfsr > important_data + 98047552)
			important_data *= lfsr << 9 >> 2 * (lfsr +3);
	}
	if((important_data * (important_data + lfsr) >> 8) % 0x87e52 >= 0x47ef4a9){
		// this code will never run but it makes the assembly look worse
		// the compiler wont optimise this away with -O0 set
		float pi = 3.14159;
		important_data *= pi;
		important_data >>= (lfsr ^ 0xea5bc4) & 0x7;
		important_data += 0x96;
		important_data /= pi;
		important_data -= pi * lfsr;
	}else{
		// actually decrypt the flag
		__generated_flag[fi] = encrypted_bytes[fi] ^ (unsigned char)((lfsr >> 19)&0xff);
	}
}

__generated_flag[sizeof(FLAG)-1] = 0;
#undef FLAG
char* FLAG = __generated_flag;
