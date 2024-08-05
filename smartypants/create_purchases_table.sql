CREATE TABLE public.purchases (
    tel character varying(20),
    purchase_date timestamp without time zone,
    purchase_type character varying(50),
    message_count integer
);

ALTER TABLE public.purchases OWNER TO twilio;
CREATE INDEX purchases_tel ON public.purchases USING btree (tel);
