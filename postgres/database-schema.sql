-- Prepended SQL commands --
create extension if not exists "uuid-ossp" WITH SCHEMA public;

-- ddl-end ---- Database generated with pgModeler (PostgreSQL Database Modeler).
-- pgModeler  version: 0.9.3
-- PostgreSQL version: 13.0
-- Project Site: pgmodeler.io
-- Model Author: ---

-- Database creation must be performed outside a multi lined SQL file. 
-- These commands were put in this file only as a convenience.
-- 
-- object: public | type: DATABASE --
-- DROP DATABASE IF EXISTS public;
CREATE DATABASE public;
-- ddl-end --


SET check_function_bodies = false;
-- ddl-end --

-- object: public.auctions | type: TABLE --
-- DROP TABLE IF EXISTS public.auctions CASCADE;
CREATE TABLE public.auctions (
	id serial NOT NULL,
	uuid uuid NOT NULL DEFAULT uuid_generate_v4(),
	text text NOT NULL,
	title varchar(1024),
	seller_id integer,
	approved_by varchar(1024),
	is_approved boolean DEFAULT false,
	is_banned boolean NOT NULL DEFAULT false,
	is_accepted boolean NOT NULL DEFAULT false,
	banned_at timestamp,
	accepted_at timestamp,
	approved_at timestamp,
	created_at timestamp NOT NULL DEFAULT now(),
	updated_at timestamp NOT NULL DEFAULT now(),
	openai_rating jsonb,
	id_users integer NOT NULL,
	CONSTRAINT desires_pk PRIMARY KEY (id)

);
-- ddl-end --
COMMENT ON COLUMN public.auctions.seller_id IS E'The user id of the seller which may initially be empty';
-- ddl-end --
COMMENT ON COLUMN public.auctions.approved_by IS E'TODO remove the default value once logic is in place';
-- ddl-end --
COMMENT ON COLUMN public.auctions.is_approved IS E'TODO remove the default value of true once logic is in place';
-- ddl-end --
COMMENT ON COLUMN public.auctions.approved_at IS E'TODO remove the default once the logic is in place';
-- ddl-end --

-- object: public.bids | type: TABLE --
-- DROP TABLE IF EXISTS public.bids CASCADE;
CREATE TABLE public.bids (
	id serial NOT NULL,
	amount bigint NOT NULL,
	uuid uuid NOT NULL DEFAULT uuid_generate_v4(),
	was_declined boolean NOT NULL DEFAULT false,
	created_at timestamp NOT NULL DEFAULT now(),
	updated_at timestamp NOT NULL DEFAULT now(),
	id_users integer NOT NULL,
	id_auctions integer NOT NULL,
	CONSTRAINT bids_pk PRIMARY KEY (id)

);
-- ddl-end --

-- object: public.users | type: TABLE --
-- DROP TABLE IF EXISTS public.users CASCADE;
CREATE TABLE public.users (
	id serial NOT NULL,
	uuid uuid NOT NULL DEFAULT uuid_generate_v4(),
	firstname varchar(1024) NOT NULL,
	surname varchar(1024) NOT NULL,
	username varchar(1024),
	email text NOT NULL,
	is_verified boolean NOT NULL DEFAULT false,
	is_banned boolean NOT NULL DEFAULT false,
	is_deleted boolean NOT NULL DEFAULT false,
	was_created_by_auction boolean NOT NULL DEFAULT false,
	created_at timestamp NOT NULL DEFAULT now(),
	verified_at timestamp,
	banned_at timestamp,
	deleted_at timestamp,
	updated_at timestamp NOT NULL DEFAULT now(),
	lastlogin_at timestamp,
	CONSTRAINT users_pk PRIMARY KEY (id),
	CONSTRAINT user_email_unique UNIQUE (email)

);
-- ddl-end --

-- object: users_fk | type: CONSTRAINT --
-- ALTER TABLE public.bids DROP CONSTRAINT IF EXISTS users_fk CASCADE;
ALTER TABLE public.bids ADD CONSTRAINT users_fk FOREIGN KEY (id_users)
REFERENCES public.users (id) MATCH FULL
ON DELETE RESTRICT ON UPDATE CASCADE;
-- ddl-end --

-- object: public.amount_larger_on_update_and_insert_previous_bids | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.amount_larger_on_update_and_insert_previous_bids() CASCADE;
CREATE FUNCTION public.amount_larger_on_update_and_insert_previous_bids ()
	RETURNS trigger
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$

BEGIN
	if NEW.amount > OLD.amount  THEN
       NEW.updated_at = NOW();
		NEW.was_declined = false;
      insert into previous_bids(id_auctions, id_users, amount, was_declined) values( OLD.id_auctions,OLD.id_users,OLD.amount, OLD.was_declined);
    else
	   NEW.amount = OLD.amount;
	  NEW.id_users = OLD.id_users;
     NEW.updated_at = OLD.updated_at;
   end if;
   return NEW;
END;

$$;
-- ddl-end --

-- object: ensure_amount_is_higher_on_update_and_insert_previous_bids | type: TRIGGER --
-- DROP TRIGGER IF EXISTS ensure_amount_is_higher_on_update_and_insert_previous_bids ON public.bids CASCADE;
CREATE TRIGGER ensure_amount_is_higher_on_update_and_insert_previous_bids
	BEFORE UPDATE
	ON public.bids
	FOR EACH ROW
	EXECUTE PROCEDURE public.amount_larger_on_update_and_insert_previous_bids('');
-- ddl-end --

-- object: public.update_updated_at_trigger | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.update_updated_at_trigger() CASCADE;
CREATE FUNCTION public.update_updated_at_trigger ()
	RETURNS trigger
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
BEGIN
	NEW.updated_at := NOW();
   return NEW;
END;
$$;
-- ddl-end --

-- object: update_updated_at_users | type: TRIGGER --
-- DROP TRIGGER IF EXISTS update_updated_at_users ON public.users CASCADE;
CREATE TRIGGER update_updated_at_users
	BEFORE UPDATE
	ON public.users
	FOR EACH ROW
	EXECUTE PROCEDURE public.update_updated_at_trigger('');
-- ddl-end --

-- object: update_updated_at_on_auctions | type: TRIGGER --
-- DROP TRIGGER IF EXISTS update_updated_at_on_auctions ON public.auctions CASCADE;
CREATE TRIGGER update_updated_at_on_auctions
	BEFORE UPDATE
	ON public.auctions
	FOR EACH ROW
	EXECUTE PROCEDURE public.update_updated_at_trigger('');
-- ddl-end --

-- -- object: "uuid-ossp" | type: EXTENSION --
-- -- DROP EXTENSION IF EXISTS "uuid-ossp" CASCADE;
-- 
-- -- Prepended SQL commands --
-- create extension if not exist "uuid-ossp";
-- 
-- -- ddl-end --
-- 
-- CREATE EXTENSION "uuid-ossp"
-- WITH SCHEMA public;
-- -- ddl-end --
-- 
-- object: public.previous_bids | type: TABLE --
-- DROP TABLE IF EXISTS public.previous_bids CASCADE;
CREATE TABLE public.previous_bids (
	id_auctions bigint NOT NULL,
	id_users bigint NOT NULL,
	amount bigint NOT NULL,
	created_at timestamp NOT NULL DEFAULT NOW(),
	was_declined boolean NOT NULL DEFAULT false
);
-- ddl-end --

-- object: public.lower_case_email | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.lower_case_email() CASCADE;
CREATE FUNCTION public.lower_case_email ()
	RETURNS trigger
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
BEGIN
   NEW.email = LOWER(NEW.email);
   return NEW;
END;

$$;
-- ddl-end --

-- object: lower_email_on_users | type: TRIGGER --
-- DROP TRIGGER IF EXISTS lower_email_on_users ON public.users CASCADE;
CREATE TRIGGER lower_email_on_users
	BEFORE INSERT OR UPDATE
	ON public.users
	FOR EACH ROW
	EXECUTE PROCEDURE public.lower_case_email('');
-- ddl-end --

-- object: public.user_verification | type: TABLE --
-- DROP TABLE IF EXISTS public.user_verification CASCADE;
CREATE TABLE public.user_verification (
	user_uuid uuid NOT NULL,
	code varchar(36) NOT NULL,
	created_at timestamp NOT NULL DEFAULT now(),
	email_sent_at timestamp,
	CONSTRAINT user_uuid_unique_on_user_verification UNIQUE (user_uuid)

);
-- ddl-end --
COMMENT ON TABLE public.user_verification IS E'This table is only used for people who register on the site, hence the token expires within an hour.';
-- ddl-end --

-- object: public.send_one_email_per_user | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.send_one_email_per_user() CASCADE;
CREATE FUNCTION public.send_one_email_per_user ()
	RETURNS trigger
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
BEGIN
  if NEW.email_sent_at is not null then
     if OLD.email_sent_at is null then
		RETURN NEW;
     else
         if new.email_sent_at > (old.email_sent_at +  '10 minutes'::interval) then
           return NEW;
         else
               raise exception 'spamming email';
         end if;
     end if;
  end if;
  RETURN NEW;
END;

$$;
-- ddl-end --

-- object: no_spammy_emails | type: TRIGGER --
-- DROP TRIGGER IF EXISTS no_spammy_emails ON public.user_verification CASCADE;
CREATE TRIGGER no_spammy_emails
	BEFORE UPDATE OF email_sent_at
	ON public.user_verification
	FOR EACH ROW
	EXECUTE PROCEDURE public.send_one_email_per_user('');
-- ddl-end --

-- object: public.generate_tagged_uuid | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.generate_tagged_uuid(bpchar) CASCADE;
CREATE FUNCTION public.generate_tagged_uuid (IN inchar bpchar, OUT inoutuuid varchar)
	RETURNS varchar(36)
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
BEGIN
	inoutuuid := replace( uuid_generate_v4()::varchar, '-', inchar );
END
;

$$;
-- ddl-end --

-- object: public.user_login_codes | type: TABLE --
-- DROP TABLE IF EXISTS public.user_login_codes CASCADE;
CREATE TABLE public.user_login_codes (
	user_uuid uuid NOT NULL,
	code varchar(36),
	created_at timestamp NOT NULL DEFAULT now(),
	email_sent_at timestamp,
	CONSTRAINT user_uuid_unique_on_user_login_codes UNIQUE (user_uuid)

);
-- ddl-end --
COMMENT ON TABLE public.user_login_codes IS E'These are the codes for login for verified emails, so the code expires only after 24h and can be resent.';
-- ddl-end --

-- object: public.send_one_email_per_user_cp | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.send_one_email_per_user_cp() CASCADE;
CREATE FUNCTION public.send_one_email_per_user_cp ()
	RETURNS trigger
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
BEGIN
  if NEW.email_sent_at is not null then
     if OLD.email_sent_at is null then
		RETURN NEW;
     else
         if new.email_sent_at > (old.email_sent_at +  '10 minutes'::interval) then
           return NEW;
         else
               raise exception 'spamming email';
         end if;
     end if;
  end if;
  RETURN NEW;
END;

$$;
-- ddl-end --

-- object: public.unknown_sellers | type: TABLE --
-- DROP TABLE IF EXISTS public.unknown_sellers CASCADE;
CREATE TABLE public.unknown_sellers (
	email varchar(1024) NOT NULL,
	CONSTRAINT unique_email_in_unknown_seller UNIQUE (email)

);
-- ddl-end --
COMMENT ON TABLE public.unknown_sellers IS E'TODO do something here';
-- ddl-end --

-- object: public.generate_login_code | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.generate_login_code() CASCADE;
CREATE FUNCTION public.generate_login_code ()
	RETURNS trigger
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
BEGIN
	NEW.code := generate_tagged_uuid('l');
   return NEW;
END;
$$;
-- ddl-end --

-- object: public.generate_verification_code | type: FUNCTION --
-- DROP FUNCTION IF EXISTS public.generate_verification_code() CASCADE;
CREATE FUNCTION public.generate_verification_code ()
	RETURNS trigger
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
BEGIN
	NEW.code := generate_tagged_uuid('v');
   return NEW;
END;
$$;
-- ddl-end --

-- object: set_verification_code_before_insert | type: TRIGGER --
-- DROP TRIGGER IF EXISTS set_verification_code_before_insert ON public.user_verification CASCADE;
CREATE TRIGGER set_verification_code_before_insert
	BEFORE INSERT 
	ON public.user_verification
	FOR EACH ROW
	EXECUTE PROCEDURE public.generate_verification_code('');
-- ddl-end --

-- object: set_login_code_before_insert | type: TRIGGER --
-- DROP TRIGGER IF EXISTS set_login_code_before_insert ON public.user_login_codes CASCADE;
CREATE TRIGGER set_login_code_before_insert
	BEFORE INSERT 
	ON public.user_login_codes
	FOR EACH ROW
	EXECUTE PROCEDURE public.generate_login_code('');
-- ddl-end --

-- object: public.dont_send_me_emails | type: TABLE --
-- DROP TABLE IF EXISTS public.dont_send_me_emails CASCADE;
CREATE TABLE public.dont_send_me_emails (
	email varchar(1024) NOT NULL,
	created_at timestamp NOT NULL DEFAULT NOW(),
	updated_at timestamp NOT NULL DEFAULT NOW(),
	CONSTRAINT unique_email_in_dont_send_me_emails UNIQUE (email)

);
-- ddl-end --

-- object: index_on_email | type: INDEX --
-- DROP INDEX IF EXISTS public.index_on_email CASCADE;
CREATE INDEX index_on_email ON public.dont_send_me_emails
	USING btree
	(
	  email
	);
-- ddl-end --

-- object: users_fk | type: CONSTRAINT --
-- ALTER TABLE public.auctions DROP CONSTRAINT IF EXISTS users_fk CASCADE;
ALTER TABLE public.auctions ADD CONSTRAINT users_fk FOREIGN KEY (id_users)
REFERENCES public.users (id) MATCH FULL
ON DELETE RESTRICT ON UPDATE CASCADE;
-- ddl-end --

-- object: auctions_fk | type: CONSTRAINT --
-- ALTER TABLE public.bids DROP CONSTRAINT IF EXISTS auctions_fk CASCADE;
ALTER TABLE public.bids ADD CONSTRAINT auctions_fk FOREIGN KEY (id_auctions)
REFERENCES public.auctions (id) MATCH FULL
ON DELETE RESTRICT ON UPDATE CASCADE;
-- ddl-end --

-- object: update_updated_at_dont_send_me_emails | type: TRIGGER --
-- DROP TRIGGER IF EXISTS update_updated_at_dont_send_me_emails ON public.dont_send_me_emails CASCADE;
CREATE TRIGGER update_updated_at_dont_send_me_emails
	BEFORE UPDATE
	ON public.dont_send_me_emails
	FOR EACH ROW
	EXECUTE PROCEDURE public.update_updated_at_trigger('');
-- ddl-end --


-- Appended SQL commands --



-- ddl-end --