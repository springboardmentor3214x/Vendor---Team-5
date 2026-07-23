import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorRanking } from './vendor-ranking';

describe('VendorRanking', () => {
  let component: VendorRanking;
  let fixture: ComponentFixture<VendorRanking>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VendorRanking],
    }).compileComponents();

    fixture = TestBed.createComponent(VendorRanking);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
