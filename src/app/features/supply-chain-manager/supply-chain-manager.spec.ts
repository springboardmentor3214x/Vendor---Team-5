import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SupplyChainManager } from './supply-chain-manager';

describe('SupplyChainManager', () => {
  let component: SupplyChainManager;
  let fixture: ComponentFixture<SupplyChainManager>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SupplyChainManager],
    }).compileComponents();

    fixture = TestBed.createComponent(SupplyChainManager);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
