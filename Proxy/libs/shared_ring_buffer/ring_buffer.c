#include  <string.h>
#include  "ring_buffer.h"

void init (ringBufS *_this)
{
    
    memset (_this, 0, sizeof (*_this));
}

int is_empty (ringBufS *_this)
{
    return (0==_this->count);
}

int is_full (ringBufS *_this)
{
    return (_this->count>=RBUF_SIZE);
}

timestamp* get (ringBufS *_this)
{
    timestamp* c;
    if (_this->count>0)
    {
      c  = &_this->buf[_this->tail];
      _this->tail = (_this->tail + 1) % RBUF_SIZE;
      --_this->count;
    }
    else
    {
      c = NULL;
    }
    return c;
}

timestamp* get_w_hash(ringBufS* _this, long hash_code)
{
	int n_searched = 0;
	int i = (_this->head - 1)%RBUF_SIZE;
	timestamp * c;

	

	while(n_searched < _this->count){
		n_searched += 1;
		if(_this->buf[i].pkt_hash_code == hash_code){
			c = &_this->buf[i];
			_this->tail = (i + 1)%RBUF_SIZE;
			if(_this->tail == _this->head){
				_this->tail = 0;
				_this->head = 0;
				_this->count = 0;
			}
			else
				_this->count = n_searched - 1;
			return c;
		}
		i  = (i - 1)%RBUF_SIZE;
	}
	return NULL;
}

void put (ringBufS *_this, timestamp* c)
{
    if (_this->count < RBUF_SIZE)
    {
      _this->buf[_this->head].secs = c->secs;
      _this->buf[_this->head].u_secs = c->u_secs;
      _this->buf[_this->head].n_secs = c->n_secs;
      _this->buf[_this->head].is_read = c->is_read;
      _this->buf[_this->head].pkt_hash_code = c->pkt_hash_code;

      _this->head = (_this->head + 1) % RBUF_SIZE;
      ++_this->count;
    }
    else{
       
       // overwrite the tail element

       _this->tail = (_this->tail + 1) % RBUF_SIZE;
       _this->buf[_this->head].secs = c->secs;
       _this->buf[_this->head].u_secs = c->u_secs;
       _this->buf[_this->head].n_secs = c->n_secs;
       _this->buf[_this->head].is_read = c->is_read;
       _this->buf[_this->head].pkt_hash_code = c->pkt_hash_code;

       _this->head = (_this->head + 1) % RBUF_SIZE;
	
    }
}

void flush (ringBufS *_this, const int clearBuffer)
{
  _this->count  = 0;
  _this->head   = 0;
  _this->tail   = 0;
  if (clearBuffer)
  {
    memset (_this->buf, 0, sizeof (_this->buf));
  }
}
