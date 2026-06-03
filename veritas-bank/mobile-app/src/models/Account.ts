// ────────────────────────────────────────────
// Account.ts  — Abstract base class
// ────────────────────────────────────────────
export abstract class Account {
  protected _accountId: number;
  protected _accountNumber: string;
  protected _accountName: string;
  protected _accountType: string;
  protected _balance: number;
  protected _currency: string;
  protected _status: string;
  protected _interestRate: number;
  protected _dailyLimit: number;
 
  constructor(data: {
    account_id: number; account_number: string;
    account_name: string; account_type: string;
    balance: number; currency: string;
    status: string; interest_rate: number;
    daily_limit: number;
  }) {
    this._accountId     = data.account_id;
    this._accountNumber = data.account_number;
    this._accountName   = data.account_name;
    this._accountType   = data.account_type;
    this._balance       = data.balance;
    this._currency      = data.currency;
    this._status        = data.status;
    this._interestRate  = data.interest_rate;
    this._dailyLimit    = data.daily_limit;
  }
 
  // Getters
  get accountId()     { return this._accountId; }
  get accountNumber() { return this._accountNumber; }
  get accountName()   { return this._accountName; }
  get accountType()   { return this._accountType; }
  get balance()       { return this._balance; }
  get status()        { return this._status; }
  get isActive()      { return this._status === 'ACTIVE'; }
  get isFrozen()      { return this._status === 'FROZEN'; }
  get maskedNumber()  { return `****${this._accountNumber.slice(-4)}`; }
 
  getFormattedBalance(): string {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency', currency: 'NGN'
    }).format(this._balance);
  }
 
  // Abstract methods — must be implemented by subclasses (Abstraction)
  abstract getAccountLabel(): string;
  abstract getMaxDailyWithdrawal(): number;
  abstract canHaveOverdraft(): boolean;
  abstract getCardColor(): string[];
 
  // Polymorphic method
  getAccountSummary(): string {
    return `${this.getAccountLabel()} | ${this.maskedNumber} | ${this.getFormattedBalance()}`;
  }
 
  toString(): string {
    return `${this._accountType}[${this._accountNumber}]: ${this.getFormattedBalance()}`;
  }
}