export type UserRole = "CUSTOMER" | "SELLER" | "ADMIN";

export type LotStatus =
  | "DRAFT"
  | "SCHEDULED"
  | "ACTIVE"
  | "TAKEN"
  | "EXPIRED"
  | "CANCELLED";

export type LotCategory =
  | "OUTERWEAR"
  | "TOPS"
  | "BOTTOMS"
  | "FOOTWEAR"
  | "ACCESSORIES";

export type OrderStatus = "PAID" | "FULFILLED" | "CANCELLED";

export interface User {
  id: string;
  email: string;
  full_name?: string | null;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface LotMeasurements {
  pit_to_pit?: number;
  length?: number;
  shoulders?: number;
  sleeve?: number;
  waist?: number;
  inseam?: number;
  hem?: number;
}

export interface LotMaterials {
  outer: string;
  lining?: string;
  hardware?: string;
}

export interface LotImage {
  id: string;
  lot_id: string;
  image_url: string;
  sort_order: number;
  display_order?: number;
  caption?: string | null;
  created_at: string;
}

export interface LotImageCreatePayload {
  image_url: string;
  sort_order?: number;
  display_order?: number;
  caption?: string | null;
}

export interface ImageUploadResponse {
  image_url: string;
  key: string;
}

export interface LotCreatePayload {
  title: string;
  brand: string;
  designer?: string | null;
  season: string;
  year: number;
  collection_name?: string | null;
  category: LotCategory;
  subcategory: string;
  tagged_size: string;
  fits_like: string;
  measurements: LotMeasurements;
  materials: LotMaterials;
  condition_rating: number;
  condition_details: string;
  country_of_origin: string;
  provenance_notes?: string | null;
  seller_location?: string;
  shipping_notes?: string;
  start_price: number;
  floor_price: number;
  step_amount: number;
  interval_seconds?: number;
  status?: LotStatus;
  images?: LotImageCreatePayload[];
}

export interface Lot {
  id: string;
  title: string;
  brand: string;
  designer: string;
  season: string;
  year: number;
  collection_name?: string | null;
  category: LotCategory;
  subcategory: string;
  tagged_size: string;
  fits_like: string;
  measurements: LotMeasurements;
  materials: LotMaterials;
  condition_rating: number;
  condition_details: string;
  country_of_origin: string;
  provenance_notes?: string | null;
  seller_location: string;
  shipping_notes: string;
  start_price: number;
  floor_price: number;
  current_price: number;
  step_amount: number;
  interval_seconds: number;
  status: LotStatus;
  started_at?: string | null;
  next_drop_at?: string | null;
  taken_at?: string | null;
  final_price?: number | null;
  winner_id?: string | null;
  images: LotImage[];
  created_at: string;
  updated_at: string;
}

export interface ShippingAddress {
  recipient_name: string;
  phone: string;
  city: string;
  postal_code: string;
  address_line: string;
  country: string;
}

export interface Order {
  id: string;
  lot_id: string;
  user_id?: string | null;
  claim_code: string;
  final_price: number;
  savings_from_ceiling: number;
  savings_percentage: number;
  status: OrderStatus;
  buyer_contact: string;
  shipping_address: ShippingAddress;
  payment_reference: string;
  created_at: string;
  lot?: Lot;
}

export interface PriceTickEvent {
  event: "PRICE_TICK";
  lot_id: string;
  current_price: number;
  floor_price: number;
  step_amount: number;
  next_drop_at: string;
}

export interface LotTakenEvent {
  event: "LOT_TAKEN";
  lot_id: string;
  final_price: number;
  taken_at: string;
  savings_percentage: number;
}

export interface LotExpiredEvent {
  event: "LOT_EXPIRED";
  lot_id: string;
  floor_price: number;
  expired_at: string;
}

export type AuctionWsEvent = PriceTickEvent | LotTakenEvent | LotExpiredEvent;
