// ============================================================
// VERITAS MICROFINANCE BANK - OOP Model Classes (TypeScript)
// Demonstrates: Encapsulation, Inheritance, Polymorphism,
//               Abstraction, Constructors, Method Overriding
// ============================================================
 
// ────────────────────────────────────────────
// Customer.ts
// ────────────────────────────────────────────
export class Customer {
  // Encapsulation: private fields
  private _customerId: number;
  private _customerCode: string;
  private _firstName: string;
  private _lastName: string;
  private _email: string;
  private _phone: string;
  private _kycLevel: number;
  private _isActive: boolean;
 
  constructor(data: {
    customer_id: number; customer_code: string;
    first_name: string; last_name: string;
    email: string; phone: string;
    kyc_level: number; is_active: string;
  }) {
    this._customerId   = data.customer_id;
    this._customerCode = data.customer_code;
    this._firstName    = data.first_name;
    this._lastName     = data.last_name;
    this._email        = data.email;
    this._phone        = data.phone;
    this._kycLevel     = data.kyc_level;
    this._isActive     = data.is_active === 'Y';
  }
 
  // Getters (controlled access)
  get customerId()   { return this._customerId; }
  get fullName()     { return `${this._firstName} ${this._lastName}`; }
  get email()        { return this._email; }
  get phone()        { return this._phone; }
  get kycLevel()     { return this._kycLevel; }
  get isActive()     { return this._isActive; }
  get customerCode() { return this._customerCode; }
 
  // Method
  getInitials(): string {
    return `${this._firstName[0]}${this._lastName[0]}`.toUpperCase();
  }
 
  toString(): string {
    return `Customer[${this._customerCode}]: ${this.fullName}`;
  }
}